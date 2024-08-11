import os
import tempfile
from typing import Any,List, Tuple, Dict, Set
from git import Repo, exc
import hashlib
from collections import defaultdict
from pygments.lexers import guess_lexer_for_filename
from pygments.util import ClassNotFound
from langchain_text_splitters import Language

class RepoCloneError(Exception):
    """Exception raised for errors in the repository cloning process."""
    pass

class FileProcessingError(Exception):
    """Exception raised for errors in processing individual files."""
    pass

def get_collections(
        repo_name: str, 
        ext_blacklist: Set[str] = set(), 
        dir_blacklist: Set[str] = set(),
        sample_ratio: float = 10,
        sample_min: int = 512,
        sample_max: int = 2048) -> Dict[str, Tuple[List[str], List[Dict[str, str]], List[str]]]:
    """
    Prepare collections of documents, document IDs, and document metadata from a GitHub repository.

    Args:
    repo_name (str): The name of the GitHub repository in the format "username/repo-name".
    ext_blacklist (Set[str]): A set of file extensions to exclude (e.g., {'.gitignore', '.dll'}).
    dir_blacklist (Set[str]): A set of directory names to exclude (e.g., {'node_modules', '.git'}).
    sample_ratio (float): Percentage of each file to read for language detection (default 10%).
    sample_min (int): Minimum number of bytes to read from each file (default 512).
    sample_min (int): Maximum number of bytes to read from each file (default 2048).

    Returns:
    Dict[str, Tuple[List[str], List[Dict[str, str]], List[str]]]: A dictionary where each key is the filetype and the value is a tuple of (document, document_id, document_metadata).
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_url = f"https://github.com/{repo_name}.git"
        try:
            repo = Repo.clone_from(repo_url, temp_dir, depth=1, single_branch=True)
        except exc.GitCommandError as e:
            raise RepoCloneError(f"Failed to clone repository {repo_name}: {str(e)}")

        collections = defaultdict(lambda: ([], [], []))

        for root, dirs, files in os.walk(temp_dir, topdown=True):
            # Exclude blacklisted directories only at the root level
            if root == temp_dir:
                dirs[:] = [d for d in dirs if d not in dir_blacklist]
                
            for file in files:
                file_path = os.path.join(root, file)
                document_id = os.path.relpath(file_path, temp_dir) # Relative path from the temp directory
                _, file_extension = os.path.splitext(file)
                # Skip files with blacklisted extensions
                if file_extension.lower() in ext_blacklist:
                    continue

                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    document = content.decode('utf-8', errors='replace') 

                    file_stat = os.stat(file_path)
                    # Calculate how many characters to use for language detection
                    sample_size = max(min(int(len(document) * sample_ratio / 100), sample_max), sample_min)
                    sample = document[:sample_size]
                    lexer = guess_lexer_for_filename(file_path, sample)
                    language = next((lang.name for lang in Language if lang.value in lexer.aliases), 'UNSUPPORTED')

                except ClassNotFound:
                    language = "UNKNOWN"

                except Exception as e:
                    raise FileProcessingError(f"Error processing file {file_path}: {str(e)}")
                
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
