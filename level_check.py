import sys
import torch
import rasterio

def geotiff_to_tensor(geotiff):
    with rasterio.open(geotiff) as data:
        image_data = data.read()  # read all bands
    tensor = torch.tensor(image_data, dtype=torch.float32)
    return tensor


def slice_tensor(tensor, slices, dim, res):
    if dim > 0:
        dim_len = tensor.size(dim-1)
        if dim_len % slices == 0:
            slice_len = dim_len // slices
        else:
            slice_len = (dim_len + 1) // slices
        sliced_tensors = torch.split(tensor, slice_len, dim-1)
        for st in sliced_tensors:
            slice_tensor(st, slices, dim-1, res)
    else:
        res.append(tensor)
        return res


#/!\ err on qgis tensors where dim(0) is 1 /!\
# fix: reshape the tensor to drop the dim(0) before splitting
def reshape_qgis_input(tensor):
    if tensor.dim() == 3 and tensor.size(0) == 1:
        tensor = tensor.reshape(tensor.size(1), tensor.size(2))
    print(f"old shape: {tensor.size()}")
    print(f"new shape: {tensor.size()}")
    return tensor

def tensor_info(tensor):
    print(f"{tensor = }")
    print(f"{tensor.size() = }")
    print(f"{tensor.dim() = }")

if len(sys.argv) != 3:
    print('missing parameter: <geotiff> <nb_splits>')
    sys.exit(1)

(_, geotiff, slices) = sys.argv

tensor = geotiff_to_tensor(geotiff)
tensor = reshape_qgis_input(tensor)

res = []
slice_tensor(tensor, int(slices), tensor.dim(), res)

print(f"{len(res) = }")

sys.exit(0)
