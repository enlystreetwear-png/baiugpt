import torch

print("PyTorch Version:", torch.__version__)

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    print("CUDA is working!")
else:
    print("CUDA is NOT working")