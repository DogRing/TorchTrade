import torch
import numpy as np
from ts.torch_handler.base_handler import BaseHandler
import json
from Model import Model,Configs

class ModelHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.initialized = False

    def initialize(self,context):
        self.manifest = context.manifest
        properties = context.system_properties
        model_dir = properties.get("model_dir")

        with open(f"{model_dir}/config.json",'r') as f:
            self.config= json.load(f)
        self.model = Model(Configs(self.config))
        state_dict = torch.load(f"{model_dir}/param.pth",map_location=torch.device('cpu'))
        self.model.load_state_dict(state_dict)
        self.model.eval()
        self.initialized = True

    def preprocess(self,data):
        input_array=np.frombuffer(data[0].get("body"),dtype=np.float64).reshape(1,-1,self.config['enc_in'])
        return torch.from_numpy(input_array).float()

    def inference(self,input_tensor):
        with torch.no_grad():
            output = self.model(input_tensor)
        return output
    
    def handle(self,data,context):
        model_input = self.preprocess(data)
        model_output=self.inference(model_input)
        return model_output.cpu().numpy().tolist()