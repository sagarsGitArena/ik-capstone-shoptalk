
import shutil
import os
from PIL import Image

def copy_file( source_folder, destination_folder,file_name):   

    print(f"User ID (UID): {os.getuid()}")  # Get the user ID
    print(f"Group ID (GID): {os.getgid()}")  # Get the group ID

    source_file = os.path.join(source_folder.strip(), file_name.strip())
    #destination_file = os.path.join(destination_folder, os.path.basename(file_name))
   
    print(f'source_file:[{source_file}]')
    print(f'destination_folder:[{destination_folder}]')   
    
    
    result = ''
    if os.path.isfile(source_file):
        try:
            print(f"Attempting to copy [{source_file}] to [{destination_folder}]")
            # Copy the specific file to the destination folder
            result = shutil.copy(source_file.strip(), destination_folder.strip())
            print(f"File successfully copied to: {result}")
            
        except FileNotFoundError:
            print(f"Error: {file_name} not found in the source folder.")
        except PermissionError:
            print(f"Error: Permission denied to copy {file_name}.")
        except shutil.Error as e:
            print(f"Error: An error occurred while copying {file_name}: {e}")
        except Exception as e:
            print(f"Unexpected error while copying {file_name}: {e}")
    else:
        print(f"Error: [{source_file}] does not exist.")
    return result


def generate_captions_batch(image_paths, device, processor, model):
    print(f"User ID (UID): {os.getuid()}")  # Get the user ID
    print(f"Group ID (GID): {os.getgid()}")  # Get the group ID
        
    """Generates captions for a batch of images."""
    images = [Image.open(path).convert("RGB") for path in image_paths]
    #inputs = processor(images=images, return_tensors="pt", padding=True)
    inputs = processor(images=images, return_tensors="pt", padding=True).to(device)
    output = model.generate(**inputs)
    captions = [processor.decode(out, skip_special_tokens=True) for out in output]
    return captions

# Function that check and returns the valid path
def validate_and_get_image_path(prefix_path, postfix_path):
    print(f"User ID (UID): {os.getuid()}")  # Get the user ID
    print(f"Group ID (GID): {os.getgid()}")  # Get the group ID
        
    fullpath = os.path.join(prefix_path, postfix_path)
    if os.path.exists(fullpath):
        return fullpath