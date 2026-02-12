import json
import os
import glob

def compound_text(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    if 'segments' in data:
        textos = []
        for key in data["segments"]:
            texto = data["segments"][key][2]
            textos.append(texto)
        return textos
    else:
        print("No annotations found in the JSON file.")
        return 0


if __name__ == "__main__":
    json_files = glob.glob(os.path.join(os.getcwd(), 'data/Dataset/**', '*.json'), recursive=True)
 
    for json_file in json_files:
        print(f"Processing file: {json_file}")
        narrative = compound_text(json_file)
        if narrative != 0:
            outputfile = json_file.replace('.json', '.txt')
            with open(outputfile, "w", encoding="utf-8") as arquivo:
                arquivo.write(" ".join(narrative))
        

