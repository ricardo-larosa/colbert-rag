import requests

# Function to get the size of a GitHub repository
def get_repo_size(repo):
    url = f"https://api.github.com/repos/{repo}"
    response = requests.get(url)
    if response.status_code == 200:
        repo_data = response.json()
        return repo_data['size']
    else:
        return None

# List of repositories
repos = [
    "astropy/astropy",
    "django/django",
    "matplotlib/matplotlib",
    "mwaskom/seaborn",
    "psf/requests",
    "pylint-dev/pylint",
    "pytest-dev/pytest",
    "scikit-learn/scikit-learn",
    "sphinx-doc/sphinx",
    "sympy/sympy"
]

# Get the sizes of the repositories
repo_sizes = {repo: get_repo_size(repo) for repo in repos}
print(repo_sizes)