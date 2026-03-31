import numpy as np

try:
    from ai_edge_litert.interpreter import Interpreter
except ImportError:
    try:
        import tflite_runtime.interpreter as tflite
        Interpreter = tflite.Interpreter
    except ImportError:
        import tensorflow as tf
        Interpreter = tf.lite.Interpreter


class KeyPointClassifier:
    def __init__(self, model_path="model/keypoint_classifier/keypoint_classifier.tflite",
                 num_threads=1):
        self.interpreter = Interpreter(model_path=model_path, num_threads=num_threads)
        self.interpreter.allocate_tensors()
        self.input_details  = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def __call__(self, landmark_list):
        self.interpreter.set_tensor(
            self.input_details[0]["index"],
            np.array([landmark_list], dtype=np.float32)
        )
        self.interpreter.invoke()
        result = self.interpreter.get_tensor(self.output_details[0]["index"])
        return int(np.argmax(np.squeeze(result)))