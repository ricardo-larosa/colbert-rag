import os
import tempfile
from typing import Any, List, Tuple, Dict, Set
from git import Repo, exc
import hashlib
from collections import defaultdict
from pygments.lexers import guess_lexer_for_filename
from pygments.util import ClassNotFound
from langchain_text_splitters import Language

def get_collections(
        repo_name: str, 
        ext_blacklist: Set[str] = set(), 
        dir_blacklist: Set[str] = set(),
        sample_ratio: float = 10,
        sample_min: int = 512,
        sample_max: int = 2048
) -> Dict[str, Tuple[List[str], List[Dict[str, str]], List[str]]]:
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_url = f"https://github.com/{repo_name}.git"
        try:
            repo = Repo.clone_from(repo_url, temp_dir, depth=1, single_branch=True)
        except exc.GitCommandError as e:
            raise Exception(f"Failed to clone repository {repo_name}: {str(e)}")

        collections: Dict[str, Tuple[List[str], List[Dict[str, str]], List[str]]] = defaultdict(lambda: ([], [], []))

        for root, dirs, files in os.walk(temp_dir, topdown=True):
            if root == temp_dir:
                dirs[:] = [d for d in dirs if d not in dir_blacklist]
                
            for file in files:
                file_path = os.path.join(root, file)
                document_id = os.path.relpath(file_path, temp_dir)
                _, file_extension = os.path.splitext(file)
                if file_extension.lower() in ext_blacklist:
                    continue

                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    document = content.decode('utf-8', errors='replace') 

                    sample_size = max(min(int(len(document) * sample_ratio / 100), sample_max), sample_min)
                    sample = document[:sample_size]
                    lexer = guess_lexer_for_filename(file_path, sample)
                    language = next((lang.name for lang in Language if lang.value in lexer.aliases), 'UNSUPPORTED')

                except ClassNotFound:
                    language = "UNKNOWN"

                except Exception as e:
                    raise Exception(f"Error processing file {file_path}: {str(e)}")
                
                document_metadata = {
                    "filename": file,
                    "path": document_id,
                    "language": language,
                    "md5_hash": hashlib.md5(content).hexdigest(),
                    "extension": file_extension,
                }

                data = (document, document_id, document_metadata)
                for i, item in enumerate(data):
                    collections[language][i].append(item)

        return dict(collections)

