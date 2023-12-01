import onnxruntime as ort
from onnxruntime.capi._pybind_state import get_available_providers


def prepare_session(model_path, *, force_cpu=False):
    
    sess_options = ort.SessionOptions()
    sess_options.intra_op_num_threads = 4
    sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_EXTENDED
    
    print(f"preparing session", flush=True)
    providers = get_available_providers()
    print(f"- available providers: {providers}")

    # reduce the providers to just what we know and want
    supported = set(['CPUExecutionProvider', 'CUDAExecutionProvider'])
    if force_cpu:
        supported = set(['CPUExecutionProvider'])

    providers = [p for p in providers if p in supported]
    
    sess = ort.InferenceSession(model_path, providers=providers, sess_options=sess_options)
    print(f"- in use providers: {sess.get_providers()}")
    
    return sess
