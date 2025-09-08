import numpy as np
import copy
class ParamMaker:

    class Section:
        def __init__(self, name: str, precision: int) -> None:
            self.params = {}
            self.precision = precision

        def get_single_float_val_string(self, val: float) -> str:
            return f"{val:.{self.precision}f}"
        
        def get_single_int_val_string(self, val: int) -> str:
            return str(val)
        
        def get_single_bool_val_string(self, val: bool) -> str:
            return "true" if val else "false"
        
        def get_single_array_val_string(self, npArray: np.ndarray) -> str:
            out_str = "{"
            str_func = None
            if np.issubdtype(npArray.dtype, np.integer):
                str_func = self.get_single_int_val_string
            elif np.issubdtype(npArray.dtype, np.floating):
                str_func = self.get_single_float_val_string
            elif np.issubdtype(npArray.dtype, np.bool_):
                str_func = self.get_single_bool_val_string
            
            for i in range(len(npArray)):
                out_str += str_func(npArray[i])
                if i != len(npArray) - 1:
                    out_str += ", "
            
            out_str += "}"
            return out_str

        def handle_array(self, npArray: np.ndarray):
            str_out = ""

            if npArray.ndim == 1:
                return self.get_single_array_val_string(npArray)
            
            if npArray.ndim > 2:
                raise ValueError("ParamMaker: Arrays with more than 2 dimensions are not supported")

            for i in range(npArray.shape[0]):
                str_out += self.get_single_array_val_string(npArray[i])
                if i != npArray.shape[0] - 1:
                    str_out += ", \n"
            
            return str_out
        
        def __setitem__(self, key, value: str):

            if isinstance(value, np.ndarray): # use only for the things that work: int, float
                self.params[key] = self.handle_array(value)
                return

            if not isinstance(key, str):
                raise ValueError("ParamMaker: Key must be a string")
            
            if not isinstance(value, str):
                raise ValueError("ParamMaker: Value must be a string or numpy array")

            self.params[key] = value

        def __getitem__(self, key):
            return self.params[key]

    def __init__(self, precision=5) -> None:
        self.sections: dict[str, ParamMaker.Section] = {}
        self.precision = precision

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise ValueError("ParamMaker: Key must be a string")

        if key not in self.sections:
            self.sections[key] = ParamMaker.Section(key, self.precision)
        return self.sections[key]

    
    def get_as_string(self):
        ret = ""
        for key, sec in self.sections.items():
            ret += f"[{key}]\n"
            for k, v in sec.params.items():
                ret += f"{k}={v};\n"
        return ret
    
    def get_as_list_of_strings(self, max_length=900):
        
        # generates parameter strings from dictionary until max_length is reached
        # returns a tuple of the generated strings and the remaining dictionary
        def gen_from_dict_until(the_dict: dict[str, ParamMaker.Section]) -> tuple[str, dict[str, ParamMaker.Section]]:
            remaining_dict = copy.deepcopy(the_dict)
            ret_str = ""
            done = False

            for key, sec in the_dict.items():
                if len(sec.params) == 0:
                    continue
                curr_sec_str = f"[{key}]\n"
                did_one_at_least = False
                for k, v in sec.params.items():
                    curr_param_str = f"{k}={v};\n"
                    if len(ret_str) + len(curr_sec_str) + len(curr_param_str) < max_length:
                        did_one_at_least = True
                        curr_sec_str += curr_param_str
                        del remaining_dict[key].params[k]
                    else:
                        done = True
                        break
                
                if did_one_at_least:
                    ret_str += curr_sec_str
                if done:
                    break
            
            secs_to_del = []
            for key, sec in remaining_dict.items():
                if len(sec.params) == 0:
                    secs_to_del.append(key)
            
            for key in secs_to_del:
                del remaining_dict[key]

            return ret_str, remaining_dict
        
        ret_list = []
        temp_dict = copy.deepcopy(self.sections)

        last_str = ""

        while len(temp_dict) > 0:
            curr_str, temp_dict = gen_from_dict_until(temp_dict)
            if curr_str == last_str:
                raise ValueError("ParamMaker: Could not generate string with this max_length")
            ret_list.append(curr_str)
            last_str = curr_str


        return ret_list





# # example usage:
# test_arr = np.linspace(0, 1e7, 100)
# test_arr = test_arr.reshape((5, 20))

# pm = ParamMaker(precision=5)
# pm["Section1"]["param1"] = test_arr

# as_string = pm.get_as_string()
