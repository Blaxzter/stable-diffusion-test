import numpy as np


if __name__ == "__main__":
    dataset = np.load(
        "E:\\Programming\\projects\\AiGenerationProjects\\StableDiffusionTest\\src\\dataset\\training_data_20250119_231048/voxels.npy",
        allow_pickle=True,
    )
    print(f"Dataset shape: {dataset.shape}")
