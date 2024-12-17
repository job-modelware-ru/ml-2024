from prep.yolo_pipeline import YOLOPipeline
import json

if __name__ == "__main__":
    with open("task_test.json", encoding="UTF-8") as json_file:
        data = json.load(json_file)
        parameters_dict = dict()
        for task in data:
            for key, value in task["constant_parameters"].items():
                parameters_dict[key] = value
            for hypothesis in task["hypotheses"]:
                for function_name, parameters in hypothesis["parameters"].items():
                    if function_name == "filter_defects" or function_name == "YOLOPipeline" or key == "form_yolo_dataset":
                        parameters_dict[function_name].update(parameters)
                    else:
                        parameters_dict[function_name] = parameters
                    for key, value in parameters.items():
                        if "fld" in key or "dst" in key:
                            parameters_dict[function_name][key] = task["task_directory"] + hypothesis[
                                "directory"] + value
                # print(parameters_dict["filter_defects"])
                YOLOPipeline(**(parameters_dict.get("YOLOPipeline"))) \
                    .filter_defects(**(parameters_dict.get("filter_defects"))) \
                    .from_supervisely_to_yolo(**(parameters_dict.get("from_supervisely_to_yolo"))) \
                    .rescale(**(parameters_dict.get("rescale"))) \
                    .split_on_tiles(**(parameters_dict.get("split_on_tiles"))) \
                    .form_yolo_dataset(**(parameters_dict.get("form_yolo_dataset"))) \
                    .run()