import os

import numpy as np
import pandas as pd

# import torchvision
from torchvision import transforms, datasets

import keras
import torch

# check if CUDA is available
train_on_gpu = torch.cuda.is_available()
print(train_on_gpu)

num_gpu = torch.cuda.device_count()
num_epochs = 4
batch_size = 64
print(f"Running on {num_gpu} GPUs")

""" 
    перераспределение данный на тренировочные и тестовые по папкам с классами согласно csv
    структура:
    tiles_images:
        train:
             img_with_defects
             img_without_defects
        test:
             img_with_defects
             img_without_defects
"""
import shutil
data = pd.read_csv(rf"D:\\pspod\\textile_data\\tiles_labels.csv")
tiles_path = rf"D:\\pspod\\textile_data\\tiles_imgs"
def change_data_dir():
    for ind, row in data.iterrows():
        img_path = row["tile_name"]
        if os.path.exists(img_path):
            img_name = row["tile_name"].split("\\")[-1]
            img_label = row["tile_label"]
            if img_label:
                new_path = os.path.join(tiles_path, "img_with_defects")
                if not os.path.exists(new_path):
                    os.makedirs(new_path)
                new_img_path = os.path.join(new_path, img_name)
                shutil.move(img_path, new_img_path)
            else:
                new_path = os.path.join(tiles_path, "img_without_defects")
                if not os.path.exists(new_path):
                    os.makedirs(new_path)
                new_img_path = os.path.join(new_path, img_name)
                shutil.move(img_path, new_img_path)

# change_data_dir()
# получаем данные из папок с изображениями

transforms = transforms.Compose([transforms.Resize(224),
                                 transforms.ToTensor()])

img_data = datasets.ImageFolder(tiles_path, transform=transforms)

def prepare_dataloader(dataset, current_gpu_index, num_gpus, batch_size):
    sampler = torch.utils.data.distributed.DistributedSampler(
        dataset,
        num_replicas=num_gpus,
        rank=current_gpu_index,
        shuffle=False,
    )
    dataloader = torch.utils.data.DataLoader(
        dataset,
        sampler=sampler,
        batch_size=batch_size,
        shuffle=False,
    )
    return dataloader


def get_model_resnet50():
    model = keras.applications.ResNet50(include_top=True,
                                        classes=2,
                                        name="resnet50")
    return model


def get_model_vgg16():
    model = keras.applications.VGG16(include_top=True,
                                     classes=2,
                                     name="VGG16")
    return model


def get_model_vgg19():
    model = keras.applications.VGG19(include_top=True,
                                     classes=2,
                                     name="VGG19")
    return model


def train_model(model, dataloader, num_epochs, optimizer, loss_fn):
    for epoch in range(num_epochs):
        running_loss = 0.0
        running_loss_count = 0
        for batch_idx, (inputs, targets) in enumerate(dataloader):
            inputs = inputs.cuda(non_blocking=True)
            targets = targets.cuda(non_blocking=True)

            outputs = model(inputs)
            loss = loss_fn(outputs, targets)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            running_loss_count += 1

        # Print loss statistics
        print(
            f"Epoch {epoch + 1}/{num_epochs}, "
            f"Loss: {running_loss / running_loss_count}"
        )


def setup_device(current_gpu_index, num_gpus):
    # Device setup
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "56492"
    device = torch.device("cuda:{}".format(current_gpu_index))
    torch.distributed.init_process_group(backend="nccl",
                                         init_method="env://",
                                         world_size=num_gpus,
                                         rank=current_gpu_index)
    torch.cuda.set_device(device)


def cleanup():
    torch.distributed.destroy_process_group()


def per_device_launch_fn(current_gpu_index, num_gpu):
    # Setup the process groups
    setup_device(current_gpu_index, num_gpu)

    dataset = img_data
    model = get_model_resnet50()

    dataloader = prepare_dataloader(dataset, current_gpu_index, num_gpu, batch_size)
  
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = torch.nn.CrossEntropyLoss()

    # Put model on device
    model = model.to(current_gpu_index)
    ddp_model = torch.nn.parallel.DistributedDataParallel(
        model, device_ids=[current_gpu_index], output_device=current_gpu_index
    )

    train_model(ddp_model, dataloader, num_epochs, optimizer, loss_fn)

    cleanup()

if __name__ == "__main__":
    torch.multiprocessing.start_processes(per_device_launch_fn,
                                          args=(num_gpu,),
                                          nprocs=num_gpu,
                                          join=True,
                                          start_method="spawn")
