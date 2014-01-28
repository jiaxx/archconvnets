python convnet.py --data-path=/export/imgnet_storage_full/yamins_skdata/sythetic_batches_0 --crop=7 --test-range=950-999 --train-range=0-50 --layer-def=/home/yamins/archconvnets/archconvnets/convnet/ut_model_full/layer_nofc_0.cfg --layer-params=/home/darren/archconvnets/archconvnets/convnet/ut_model_full/layer-params.cfg --data-provider=general-cropped --test-freq=10 --conserve-mem=1 --max-filesize=99999999  --img-size=128 --save-db=1 --experiment-data='{"experiment_id": "mytestrun2"}' --dp-params='{"perm_type": "random", "perm_seed": 0, "preproc": {"normalize": false, "dtype": "float32", "resize_to": [128, 128, 3], "mode": "RGB"}, "batch_size": 128, "meta_attribute": "obj", "dataset_name": ["dldata.stimulus_sets.synthetic.synthetic_datasets", "TrainingDataset"]}'

