import json
import h5py
import tensorflow as tf
from tensorflow.keras.models import model_from_json, Sequential, Model
from tensorflow.keras.layers import BatchNormalization, InputLayer, Conv2D

def fix_batch_norm_axis(model_config):
    """
    Fixes the 'axis' parameter in all BatchNormalization layers from a list to an integer.
    """
    for layer in model_config['config']['layers']:
        if layer['class_name'] == 'BatchNormalization':
            axis = layer['config'].get('axis')
            if isinstance(axis, list):
                original_axis = axis.copy()
                layer['config']['axis'] = axis[0]
                print(f"Fixed BatchNormalization axis from {original_axis} to {layer['config']['axis']}")
    return model_config

def fix_class_name(model_config):
    """
    Fixes 'Functional' class_name to 'Model' in the model configuration.
    """
    def traverse_layers(layers):
        for layer in layers:
            if layer['class_name'] == 'Functional':
                print(f"Changing class_name from 'Functional' to 'Model' for layer: {layer.get('name', 'Unnamed')}")
                layer['class_name'] = 'Model'
            # Recursively traverse nested layers if any
            if 'layers' in layer['config']:
                traverse_layers(layer['config']['layers'])
    
    traverse_layers(model_config['config']['layers'])
    return model_config

def load_and_fix_model(original_model_path, fixed_model_path):
    """
    Loads the original model, fixes the BatchNormalization layers and class names, and saves the fixed model.
    """
    with h5py.File(original_model_path, 'r') as f:
        # Load the model configuration
        model_config = f.attrs.get('model_config')
        if model_config is None:
            raise ValueError('No model_config found in the H5 file')
        
        # Decode if necessary (Python 3 strings)
        if isinstance(model_config, bytes):
            model_config = model_config.decode('utf-8')
        
        # Load JSON
        model_config = json.loads(model_config)

        # Fix the axis in BatchNormalization layers
        model_config = fix_batch_norm_axis(model_config)

        # Fix class_name from 'Functional' to 'Model'
        model_config = fix_class_name(model_config)

        # Convert back to JSON string
        fixed_model_config = json.dumps(model_config)

    # Reconstruct the model from the fixed configuration with custom_objects
    model = model_from_json(fixed_model_config, custom_objects={'Sequential': Sequential, 'Model': Model})

    # Load weights
    model.load_weights(original_model_path)

    # Save the fixed model to a new file
    model.save(fixed_model_path)
    print(f"Fixed model saved to {fixed_model_path}")

if __name__ == "__main__":
    original_model = '/Users/sefacahyir/Plant-Disease-Detection/myModel.h5'
    fixed_model = '/Users/sefacahyir/Plant-Disease-Detection/fixed_myModel.h5'
    load_and_fix_model(original_model, fixed_model)