import logging
import tensorflow as tf
from cunet.train.others.utilities import (
    make_earlystopping, make_reduce_lr, make_tensorboard, make_checkpoint,
    make_name, save_dir, write_config
)
from cunet.train.config import config
from cunet.train.models.cunet_model import cunet_model
from cunet.train.models.unet_model import unet_model
import os

#from cunet.train.others.lock import get_lock


#logger = tf.get_logger()
#logger.setLevel(logging.INFO)


def main():
    config.parse_args()
    name = make_name()
    save_path = save_dir('models', name)
    write_config(save_path)
    #_ = get_lock()
    #logger.info('Starting the computation')

    #logger.info('Running training with config %s' % str(config))
    #logger.info('Getting the model')
    if config.MODE == 'standard':
        model = unet_model()
    if config.MODE == 'conditioned':
        model = cunet_model()
    latest = tf.train.latest_checkpoint(
        os.path.join(save_path, 'checkpoint'))
    if latest:
        model.load_weights(latest)
        #logger.info("Restored from {}".format(latest))
    #else:
        #logger.info("Initializing from scratch.")

    #logger.info('Preparing the genrators')
    # Here to be sure that has the same config
    from cunet.train.data_loader import dataset_generator
    ds_train = dataset_generator()
    ds_val = dataset_generator(val_set=True)

    #logger.info('Starting training for %s' % name)

    # USE VAL_STEPS!!

    total_parameters = 0
    for variable in tf.trainable_variables():
        # shape is an array of tf.Dimension
        shape = variable.get_shape()
        print(shape)
        print(len(shape))
        variable_parameters = 1
        for dim in shape:
            print(dim)
            variable_parameters *= dim.value
        print(variable_parameters)
        total_parameters += variable_parameters
    print("TOTAL PARAMETERS: "+str(total_parameters))
    
    model.fit(
        ds_train,
        validation_data=ds_val,
        steps_per_epoch=config.N_BATCH,
        epochs=config.N_EPOCH,
        verbose=1,
        validation_steps=config.N_BATCH//2,
        callbacks=[
            #make_earlystopping(),
            make_reduce_lr(),
            make_tensorboard(save_path),
            make_checkpoint(save_path)
        ])

    #logger.info('Saving model %s' % name)
    model.save(os.path.join(save_path, name+'.h5'))
    #logger.info('Done!')
    return


if __name__ == '__main__':
    main()
