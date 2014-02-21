import numpy.random as nr
import json
import cPickle
import hashlib
import subprocess
import tempfile

import hyperopt
try:
    from hyperopt.pyll import scope
except ImportError:
    print 'Trying standalone pyll'
    from pyll import scope

from ..convnet.gpumodel import IGPUModel
from ..convnet.convnet import ConvNet
from ..convnet.api import odict_to_config

from . import cifar_params
from .hyperopt_helpers import suggest_multiple_from_name


def cifar_random_experiment0(experiment_id):
    dbname = 'cifar_predictions_random_experiment0'
    host = 'localhost'
    port = 22334
    bandit = 'cifar_prediction_bandit'
    bandit_kwargdict = {'param_args': {}, 'experiment_id': experiment_id}
    exp = cifar_random_experiment(dbname, host, port, bandit, bandit_kwargdict)
    return exp


def cifar_random_experiment(dbname, host, port, bandit, bandit_kwargdict):
    num = 1
    bandit_algo_names = ['hyperopt.Random'] * num
    bandit_names = ['archconvnets.hyperopt.cifar_prediction.%s' % bandit] * num
    ek = hashlib.sha1(cPickle.dumps(bandit_kwargdict)).hexdigest()
    exp_keys = ['cifar_prediction_random_%s_%s_%i' % (bandit, ek, i) for i in range(num)]
    bandit_args_list = [(bandit_kwargdict,) for i in range(num)]
    bandit_kwargs_list = [{} for i in range(num)]
    return suggest_multiple_from_name(dbname=dbname,
                               host=host,
                               port=port,
                               bandit_algo_names=bandit_algo_names,
                               bandit_names=bandit_names,
                               exp_keys=exp_keys,
                               N=None,
                               bandit_args_list=bandit_args_list,
                               bandit_kwargs_list=bandit_kwargs_list,
                               bandit_algo_args_list=[() for _i in range(num)],
                               bandit_algo_kwargs_list=[{} for _i in range(num)])


@hyperopt.base.as_bandit(exceptions=[])
def cifar_prediction_bandit(argdict):
    template = cifar_params.template_func(argdict['param_args'])
    return scope.cifar_prediction_bandit_evaluate(template, argdict)


@scope.define
def cifar_prediction_bandit_evaluate(config, kwargs, features=None):
    _, layer_fname = tempfile.mkstemp()
    odict_to_config(config['layer_def'], savepath=layer_fname)
    _, layer_param_fname = tempfile.mkstemp()
    odict_to_config(config['learning_params'], savepath=layer_param_fname)

    tf = 20*6 / 20
    epochs = 2
    exp_id = kwargs['experiment_id']

    crop = 4
    fs_name = 'cifar_prediction'
    config_str = json.dumps(config)
    config_id = hashlib.sha1(config_str).hexdigest()
    exp_str = json.dumps({"experiment_id": exp_id,
                          "config": config,
                          "config_id": config_id})
    
    op = ConvNet.get_options_parser()
    oppdict = [('--save-db', '1'),
               ('--crop', '4'),
               ('--train-range', '0-4'),
               ('--test-range', '5'),
               ('--layer-def', layer_fname),
               ('--layer-params', layer_param_fname),
               ('--data-provider', 'general-cropped'),
               ('--dp-params', '{"preproc": {"normalize": false, "dtype": "float32", "mask": null, "crop": null, "resize_to": [32, 32], "mode": "RGB"}, "batch_size": 10000, "meta_attribute": "category", "dataset_name":["dldata.stimulus_sets.cifar10", "Cifar10"]}'),
               ('--test-freq', '6'),
               ('--epochs', '20'),
               ('--img-size', '32'),
               ('--experiment-data', exp_str),
               ("--checkpoint-fs-name", fs_name)]

    #cmd_tmpl  = """python convnet.py --crop=%d --test-range=0-4 --train-range=5 --layer-def=%s --layer-params=%s --data-provider=general-cropped  --dp-params='{"preproc": {"normalize": false, "dtype": "float32", "mask": null, "crop": null, "resize_to": [32, 32], "mode": "RGB"}, "batch_size": 10000, "meta_attribute": "category", "dataset_name":["dldata.stimulus_sets.cifar10", "Cifar10"]}' --test-freq=%d --epochs=%d --save-db=1 --img-size=32 --experiment-data='{"experiment_id":"%s", "config":%s, "config_id":"%s"}' --checkpoint-fs-name=%s"""  % (crop, layer_fname, layer_param_fname, tf, epochs, exp_id, config_str, config_id, fs_name)
    #retcode = subprocess.call(cmd_tmpl, shell=True)

    op, load_dic = IGPUModel.parse_options(op, input_opts=dict(oppdict), ignore_argv=True)
    nr.seed(0)
    model = ConvNet(op, load_dic)
    model.start()
    
    cpt = IGPUModel.load_checkpoint_from_db({"experiment_id":exp_id, "config_id": config_id}, checkpoint_fs_host='localhost', checkpoint_fs_port=27017, checkpoint_db_name='convnet_checkpoint_db', checkpoint_fs_name=fs_name, only_rec=True)
    rec = cpt['rec']
    rec['kwargs'] = kwargs
    rec['loss'] = rec['test_outputs'][0]['logprob'][0]
    rec['status'] = 'ok'

    return rec
