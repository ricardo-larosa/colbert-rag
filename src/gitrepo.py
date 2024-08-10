import os
import tempfile
from typing import Any,List, Tuple, Dict, Set
from git import Repo, exc
import time
import hashlib
from collections import defaultdict
from pygments.lexers import guess_lexer_for_filename
from pygments.util import ClassNotFound

class RepoCloneError(Exception):
    """Exception raised for errors in the repository cloning process."""
    pass

class FileProcessingError(Exception):
    """Exception raised for errors in processing individual files."""
    pass

def get_repo(
        repo_name: str, 
        ext_blacklist: Set[str] = set(), 
        dir_blacklist: Set[str] = set(),
        sample_ratio: float = 10,
        sample_min: int = 512,
        sample_max: int = 2048) -> Dict[str, Tuple[List[str], List[Dict[str, Any]], List[str]]]:
    """
    Clone a GitHub repository and read its contents, excluding files with blacklisted extensions.

    Args:
    repo_name (str): The name of the GitHub repository in the format "username/repo-name".
    ext_blacklist (Set[str]): A set of file extensions to exclude (e.g., {'.exe', '.dll'}).
    dir_blacklist (Set[str]): A set of directory names to exclude (e.g., {'node_modules', 'build'}).
    sample_ratio (float): Percentage of each file to read for language detection (default 10%).
    sample_min (int): Minimum number of bytes to read from each file (default 100).
    sample_min (int): Maximum number of bytes to read from each file (default 1000).

    Returns:
    Dict[str, Tuple[List[str], List[Dict[str, Any]], List[str]]]: A dictionary where each key is the filetype and the value is a tuple of (file_contents, metadata, ids).
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Clone the repository, fetching only the default branch
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
                relative_path = os.path.relpath(file_path, temp_dir)
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
                    sample_size = max(min(int(len(document) * sample_percentage / 100), max_chars), min_chars)
                    sample = document[:sample_size]
                    lexer = guess_lexer_for_filename(file_path, sample)
                    language = lexer.name.lower()

                except ClassNotFound:
                    language = "unknown"

                except Exception as e:
                    raise FileProcessingError(f"Error processing file {file_path}: {str(e)}")
                
                file_meta = {
                    "filename": file,
                    "path": relative_path,
                    "size_bytes": file_stat.st_size,
                    "language": language,
                    "md5_hash": hashlib.md5(content).hexdigest(),
                    "extension": file_extension,
                }

                collections[language][0].append(document) # collection
                collections[language][1].append(relative_path) # document_id
                collections[language][2].append(file_meta) # document _metadata

        return dict(collections) 
