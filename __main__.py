import argparse
import logging
import shutil 
import concurrent.futures
from pathlib import Path
from time import perf_counter
from normalize import normalize


REGISTER_EXTENSIONS = {
    'JPEG': 'images',
    'PNG': 'images',
    'JPG': 'images',
    'SVG': 'images',
    'AVI': 'video',
    'MP4': 'video',
    'MOV': 'video',
    'MKV': 'video',
    'DOC': 'documents',
    'DOCX': 'documents',
    'TXT': 'documents',
    'PDF': 'documents',
    'XLSX': 'documents',
    'PPTX': 'documents',
    'MP3': 'audio',
    'OGG': 'audio',
    'WAV': 'audio',
    'AMR': 'audio',
    'GZ': 'archives',
    'TAR': 'archives',
    'ZIP': 'archives',
    }

FOLDERS = []

parser = argparse.ArgumentParser(description='App for Sorting  folders')

parser.add_argument('--start', required=True)     
parser.add_argument('--finish', default='dist')
args = vars(parser.parse_args())                    
source = args.get('start')
output = args.get('finish')



def get_extension(file_name: str) -> str:
    return Path(file_name).suffix[1:].upper()

def find_folders(path:Path):
    for element in path.iterdir():
        if element.is_dir():
            FOLDERS.append(element)
            find_folders(element)

def archiv(folder, filename):
        final_folder = folder / normalize(filename.name.replace(filename.suffix, ''))
        final_folder.mkdir(exist_ok=True, parents=True)
        try:
            shutil.unpack_archive(str(filename.resolve()), str(final_folder.resolve()))
        except shutil.ReadError:
            final_folder.rmdir()
            return None
        filename.unlink()

def moving_files(path: Path):
    for file_ in path.iterdir(): 
        if file_.is_file():
            ext = get_extension(file_.name)
            new_folder = REGISTER_EXTENSIONS.get(ext)
            if new_folder:
                new_path = output_folder / new_folder / ext
            else:
                new_path = output_folder / 'OTHER'
            try: 
                if new_folder == 'archives':
                    archiv(new_path, file_)
                else:    
                    new_path.mkdir(exist_ok=True, parents=True)
                    shutil.copyfile(file_, new_path / normalize(file_.name))
                # logging.debug('The folder has been processed ')
            except OSError as e:
                logging.debug(e)
               

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="%(threadName)s %(message)s")   
    base_folder = Path(source)     
    output_folder = Path(output)

    start_time = perf_counter()

    FOLDERS.append(base_folder)
    find_folders(base_folder)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(moving_files, FOLDERS)
    end_time = perf_counter()

    print(f'Working is {end_time - start_time: 0.2f} seconds.')     