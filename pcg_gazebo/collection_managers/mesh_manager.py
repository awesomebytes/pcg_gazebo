# Copyright (c) 2020 - The Procedural Generation for Gazebo authors
# For information on the respective copyright owner see the NOTICE file
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
from ._collection_manager import _CollectionManager
from ..simulation.properties import Mesh
from ..path import Path
from ..log import PCG_ROOT_LOGGER
from ..utils import is_array
import trimesh


class MeshManager(_CollectionManager):
    def __init__(self):
        super(MeshManager, self).__init__()

    @staticmethod
    def get_instance():
        if MeshManager._INSTANCE is None:
            MeshManager._INSTANCE = MeshManager()
        return MeshManager._INSTANCE

    def get_unique_tag(self, length=5):
        i = 0
        label = 'mesh_{}'.format(i)
        while self.has_element(label):
            i += 1
            label = 'mesh_{}'.format(i)
        return label

    def add(self, tag=None, **kwargs):
        if tag is None:
            tag = self.get_unique_tag()
        if self.has_element(tag):
            return tag
        self._collection[tag] = dict(filename=None)
        if 'filename' in kwargs:
            assert os.path.isfile(kwargs['filename']), \
                'Invalid mesh filename, value={}'.format(kwargs['filename'])
            cur_tag = self.find_mesh_by_filename(kwargs['filename'])
            if cur_tag is not None:
                return cur_tag
            self._collection[tag]['filename'] = Path(kwargs['filename'])
            self._collection[tag]['mesh'] = trimesh.load_mesh(
                kwargs['filename'])
            if isinstance(self._collection[tag]['mesh'], trimesh.Scene):
                meshes = list(self._collection[tag]['mesh'].dump())
                PCG_ROOT_LOGGER.info('# meshes={}, filename={}'.format(
                    len(meshes), self._collection[tag]['filename']))
                if len(meshes) == 1:
                    self._collection[tag]['mesh'] = meshes[0]
        elif 'mesh' in kwargs:
            self._collection[tag]['mesh'] = kwargs['mesh']
            if isinstance(self._collection[tag]['mesh'], trimesh.Scene):
                meshes = list(self._collection[tag]['mesh'].dump())
                PCG_ROOT_LOGGER.info('# meshes={}'.format(
                    len(meshes)))
                if len(meshes) == 1:
                    self._collection[tag]['mesh'] = meshes[0]
        elif 'type' in kwargs:
            if kwargs['type'] == 'box' and 'size' in kwargs:
                assert is_array(kwargs['size']), \
                    'Size is not an array'
                vec = list(kwargs['size'])
                assert len(vec) == 3, 'Input size array must have 3 elements'
                for elem in vec:
                    assert elem > 0, \
                        'Size vector components must be greater than zero'

                self._collection[tag]['mesh'] = \
                    trimesh.creation.box(extents=kwargs['size'])
                PCG_ROOT_LOGGER.info('Box mesh created, size={}'.format(
                    kwargs['size']))
            elif kwargs['type'] == 'cylinder' and \
                    'radius' in kwargs and \
                    'height' in kwargs:
                assert kwargs['radius'] > 0, \
                    'Cylinder radius must be greater than zero'
                assert kwargs['height'] > 0, \
                    'Cylinder height must be greater than zero'
                self._collection[tag]['mesh'] = \
                    trimesh.creation.cylinder(
                        radius=kwargs['radius'],
                        height=kwargs['height'])
                PCG_ROOT_LOGGER.info(
                    'Cylinder mesh created, radius [m]={},'
                    ' height [m]={}'.format(
                        kwargs['radius'], kwargs['height']))
            elif kwargs['type'] == 'capsule' and \
                    'radius' in kwargs and \
                    'height' in kwargs:
                self._collection[tag]['mesh'] = Mesh.create_capsule(
                    radius=kwargs['radius'],
                    height=kwargs['height']
                )
                assert kwargs['radius'] > 0, \
                    'Capsule radius must be greater than zero'
                assert kwargs['height'] > 0, \
                    'Capsule height must be greater than zero'
                self._collection[tag]['mesh'] = \
                    trimesh.creation.capsule(
                        radius=kwargs['radius'],
                        height=kwargs['height'])
                PCG_ROOT_LOGGER.info(
                    'Capsule mesh created, radius [m]={},'
                    ' height [m]={}'.format(
                        kwargs['radius'], kwargs['height']))
            elif kwargs['type'] == 'sphere' and \
                    'radius' in kwargs:
                assert kwargs['radius'] > 0, \
                    'Sphere radius must be greater than zero'
                self._collection[tag]['mesh'] = \
                    trimesh.creation.icosphere(radius=kwargs['radius'])
                PCG_ROOT_LOGGER.info(
                    'Sphere mesh created, radius [m]={}'.format(
                        kwargs['radius']))
            else:
                del self._collection[tag]
                return None
        else:
            del self._collection[tag]
            return None
        return tag

    def get(self, **kwargs):
        if 'filename' in kwargs:
            mesh_filename = Path(kwargs['filename'])

            for tag in self._collection:
                if self._collection[tag]['filename']._uri == mesh_filename:
                    return self._collection[tag]['mesh']
        elif 'tag' in kwargs:
            if not self.has_element(kwargs['tag']):
                PCG_ROOT_LOGGER.error(
                    'No element with tag <{}> was found'.format(
                        kwargs['tag']))
                return None
            return self._collection[kwargs['tag']]['mesh']
        return None

    def find_mesh_by_filename(self, filename):
        mesh_filename = Path(filename)
        if mesh_filename is None:
            return None
        for tag in self._collection:
            if self._collection[tag]['filename'] is not None:
                if self._collection[tag]['filename'] == mesh_filename:
                    return tag
        return None