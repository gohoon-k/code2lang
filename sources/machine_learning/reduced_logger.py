from keras.callbacks import Callback


class ReducedLogger(Callback):

    def on_epoch_end(self, epoch, logs=None):
        if epoch == 0 or (epoch + 1) % 15 == 0:
            print(f"epoch {epoch + 1:03d}/{self.params['epochs']}  ->  loss: {logs['loss']:.05f}, val_loss: {logs['val_loss']:.05f}")
