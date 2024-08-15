import sys
import os

proto_dir = os.path.dirname(os.path.abspath(__file__))
if proto_dir not in sys.path:
    sys.path.insert(0, proto_dir)

from . import colbertrag_pb2
from . import colbertrag_pb2_grpc

# Re-export the modules
__all__ = ['colbertrag_pb2', 'colbertrag_pb2_grpc']
