"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
from functools import partial

from qgis.PyQt.QtCore import QPoint
from qgis.PyQt.QtGui import QColor
from qgis.core import QgsProject, QgsPointXY,  QgsVectorLayer, QgsPointLocator, QgsSnappingConfig, QgsSnappingUtils, \
    QgsTolerance, QgsFeatureRequest
from qgis.gui import QgsVertexMarker, QgsMapCanvas, QgsMapToolEmitPoint

from ... import global_vars
from ...lib import tools_qgis


class GwSnapManager(object):

    def __init__(self, iface):
        """ Class constructor """

        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.previous_snapping = None
        self.is_valid = False
        self.point_xy = {}

        # Snapper
        self.snapping_config = self.get_snapping_options()
        self.snapping_config.setEnabled(True)
        self.snapper = self.get_snapper()
        proj = QgsProject.instance()
        proj.writeEntry('Digitizing', 'SnappingMode', 'advanced')

        # Set default vertex marker
        color = QColor(255, 100, 255)
        self.vertex_marker = QgsVertexMarker(self.canvas)
        self.vertex_marker.setIconType(QgsVertexMarker.ICON_CROSS)
        self.vertex_marker.setColor(color)
        self.vertex_marker.setIconSize(15)
        self.vertex_marker.setPenWidth(3)


    def init_snapping_config(self):
        pass


    def set_snapping_layers(self):
        """ Set main snapping layers """

        self.layer_arc = tools_qgis.get_layer_by_tablename('v_edit_arc')
        self.layer_connec = tools_qgis.get_layer_by_tablename('v_edit_connec')
        self.layer_gully = tools_qgis.get_layer_by_tablename('v_edit_gully')
        self.layer_node = tools_qgis.get_layer_by_tablename('v_edit_node')


    def get_snapping_options(self):
        """ Function that collects all the snapping options """

        global_snapping_config = QgsProject.instance().snappingConfig()
        return global_snapping_config


    def store_snapping_options(self):
        """ Store the project user snapping configuration """

        # Get an array containing the snapping options for all the layers
        self.previous_snapping = self.get_snapping_options()


    def set_snapping_status(self, enable=False):
        """ Enable/Disable snapping of all layers """

        QgsProject.instance().blockSignals(True)

        layers = tools_qgis.get_project_layers()
        # Loop through all the layers in the project
        for layer in layers:
            if type(layer) != QgsVectorLayer:
                continue
            layer_settings = self.snapping_config.individualLayerSettings(layer)
            layer_settings.setEnabled(enable)
            self.snapping_config.setIndividualLayerSettings(layer, layer_settings)

        QgsProject.instance().blockSignals(False)
        QgsProject.instance().snappingConfigChanged.emit(self.snapping_config)


    def set_snap_mode(self, mode=3):
        """ Defines on which layer the snapping is performed
        :param mode: 1 = ActiveLayer, 2=AllLayers, 3=AdvancedConfiguration (int or SnappingMode)
        """

        snapping_options = self.get_snapping_options()
        if snapping_options:
            QgsProject.instance().blockSignals(True)
            snapping_options.setMode(mode)
            QgsProject.instance().setSnappingConfig(snapping_options)
            QgsProject.instance().blockSignals(False)
            QgsProject.instance().snappingConfigChanged.emit(snapping_options)


    def config_snap_to_arc(self):
        """ Set snapping to 'arc' """

        QgsProject.instance().blockSignals(True)
        self.set_snapping_layers()
        layer_settings = self.config_snap_to_layer(self.layer_arc, QgsPointLocator.All, True)
        if layer_settings:
            layer_settings.setType(2)
            layer_settings.setTolerance(15)
            layer_settings.setEnabled(True)
        else:
            layer_settings = QgsSnappingConfig.IndividualLayerSettings(True, 2, 15, 1)
        self.snapping_config.setIndividualLayerSettings(self.layer_arc, layer_settings)
        self.restore_snap_options(self.snapping_config)


    def config_snap_to_node(self):
        """ Set snapping to 'node' """

        QgsProject.instance().blockSignals(True)
        layer_settings = self.config_snap_to_layer(self.layer_node, QgsPointLocator.Vertex, True)
        if layer_settings:
            layer_settings.setType(1)
            layer_settings.setTolerance(15)
            layer_settings.setEnabled(True)
        else:
            layer_settings = QgsSnappingConfig.IndividualLayerSettings(True, 1, 15, 1)
        self.snapping_config.setIndividualLayerSettings(self.layer_node, layer_settings)
        self.restore_snap_options(self.snapping_config)


    def config_snap_to_connec(self):
        """ Set snapping to 'connec' and 'gully' """

        QgsProject.instance().blockSignals(True)
        snapping_config = self.get_snapping_options()
        layer_settings = self.config_snap_to_layer(tools_qgis.get_layer_by_tablename('v_edit_connec'), QgsPointLocator.Vertex, True)
        if layer_settings:
            layer_settings.setType(1)
            layer_settings.setTolerance(15)
            layer_settings.setEnabled(True)
        else:
            layer_settings = QgsSnappingConfig.IndividualLayerSettings(True, 1, 15, 1)
        snapping_config.setIndividualLayerSettings(tools_qgis.get_layer_by_tablename('v_edit_connec'), layer_settings)
        self.restore_snap_options(self.snapping_config)


    def config_snap_to_gully(self):

        QgsProject.instance().blockSignals(True)
        snapping_config = self.get_snapping_options()
        layer_settings = self.config_snap_to_layer(tools_qgis.get_layer_by_tablename('v_edit_gully'), QgsPointLocator.Vertex, True)
        if layer_settings:
            layer_settings.setType(1)
            layer_settings.setTolerance(15)
            layer_settings.setEnabled(True)
        else:
            layer_settings = QgsSnappingConfig.IndividualLayerSettings(True, 1, 15, 1)
        snapping_config.setIndividualLayerSettings(tools_qgis.get_layer_by_tablename('v_edit_gully'), layer_settings)
        self.restore_snap_options(self.snapping_config)


    def config_snap_to_layer(self, layer, point_locator=QgsPointLocator.All, set_settings=False):
        """ Set snapping to @layer """

        if layer is None:
            return

        QgsSnappingUtils.LayerConfig(layer, point_locator, 15, QgsTolerance.Pixels)
        if set_settings:
            layer_settings = self.snapping_config.individualLayerSettings(layer)
            layer_settings.setEnabled(True)
            self.snapping_config.setIndividualLayerSettings(layer, layer_settings)
            return layer_settings


    def restore_snap_options(self, snappings_options):
        """ Function that applies selected snapping configuration """

        QgsProject.instance().blockSignals(True)
        if snappings_options is None and self.snapping_config:
            snappings_options = self.snapping_config
        QgsProject.instance().setSnappingConfig(snappings_options)
        QgsProject.instance().blockSignals(False)
        QgsProject.instance().snappingConfigChanged.emit(self.snapping_config)


    def recover_snapping_options(self):
        """ Function to restore the previous snapping configuration """

        self.restore_snap_options(self.previous_snapping)


    def get_snapper(self):
        """ Return snapper """

        snapper = QgsMapCanvas.snappingUtils(self.canvas)
        return snapper


    def snap_to_current_layer(self, event_point, vertex_marker=None):

        self.is_valid = False
        if event_point is None:
            return None, None

        result = self.snapper.snapToCurrentLayer(event_point, QgsPointLocator.All)
        if vertex_marker:
            if result.isValid():
                # Get the point and add marker on it
                point = QgsPointXY(result.point())
                vertex_marker.setCenter(point)
                vertex_marker.show()

        self.is_valid = result.isValid()
        return result


    def snap_to_project_config_layers(self, event_point, vertex_marker=None):

        self.is_valid = False
        if event_point is None:
            return None, None

        result = self.snapper.snapToMap(event_point)
        if vertex_marker:
            if result.isValid():
                # Get the point and add marker on it
                point = QgsPointXY(result.point())
                vertex_marker.setCenter(point)
                vertex_marker.show()

        self.is_valid = result.isValid()
        return result


    def add_marker(self, result, vertex_marker=None, icon_type=None):

        if not result.isValid():
            return None

        if vertex_marker is None:
            vertex_marker = self.vertex_marker

        point = result.point()
        if icon_type:
            vertex_marker.setIconType(icon_type)
        vertex_marker.setCenter(point)
        vertex_marker.show()

        return point


    def remove_marker(self, vertex_marker=None):

        if vertex_marker is None:
            vertex_marker = self.vertex_marker

        vertex_marker.hide()


    def get_event_point(self, event=None, point=None):
        """ Get point """

        event_point = None
        x = None
        y = None
        try:
            if event:
                x = event.pos().x()
                y = event.pos().y()
            if point:
                map_point = self.canvas.getCoordinateTransform().transform(point)
                x = map_point.x()
                y = map_point.y()
            event_point = QPoint(x, y)
        except:
            pass
        finally:
            return event_point


    def get_snapped_layer(self, result):

        layer = None
        if result.isValid():
            layer = result.layer()

        return layer


    def get_snapped_point(self, result):

        point = None
        if result.isValid():
            point = QgsPointXY(result.point())

        return point


    def get_snapped_feature_id(self, result):

        feature_id = None
        if result.isValid():
            feature_id = result.featureId()

        return feature_id


    def get_snapped_feature(self, result, select_feature=False):

        if not result.isValid():
            return None

        snapped_feat = None
        try:
            layer = result.layer()
            feature_id = result.featureId()
            feature_request = QgsFeatureRequest().setFilterFid(feature_id)
            snapped_feat = next(layer.getFeatures(feature_request))
            if select_feature and snapped_feat:
                self.select_snapped_feature(result, feature_id)
        except:
            pass
        finally:
            return snapped_feat


    def select_snapped_feature(self, result, feature_id):

        if not result.isValid():
            return

        layer = result.layer()
        layer.select([feature_id])


    def result_is_valid(self):
        return self.is_valid


    def add_point(self, vertex_marker):
        """ Create the appropriate map tool and connect to the corresponding signal """

        active_layer = global_vars.iface.activeLayer()
        if active_layer is None:
            active_layer = tools_qgis.get_layer_by_tablename('version')
            global_vars.iface.setActiveLayer(active_layer)

        # Vertex marker
        vertex_marker.setColor(QColor(255, 100, 255))
        vertex_marker.setIconSize(15)
        vertex_marker.setIconType(QgsVertexMarker.ICON_CROSS)
        vertex_marker.setPenWidth(3)

        # Snapper
        emit_point = QgsMapToolEmitPoint(global_vars.canvas)
        global_vars.canvas.setMapTool(emit_point)
        global_vars.canvas.xyCoordinates.connect(partial(self.get_mouse_move, vertex_marker))
        emit_point.canvasClicked.connect(partial(self.get_xy, vertex_marker, emit_point))


    def get_mouse_move(self, vertex_marker, point):

        # Hide marker and get coordinates
        vertex_marker.hide()
        event_point = self.get_event_point(point=point)

        # Snapping
        result = self.snap_to_project_config_layers(event_point)
        if result.isValid():
            self.add_marker(result, vertex_marker)
        else:
            vertex_marker.hide()


    def get_xy(self, vertex_marker, emit_point, point):
        """ Get coordinates of selected point """

        # Setting x, y coordinates from point
        self.point_xy['x'] = point.x()
        self.point_xy['y'] = point.y()

        message = "Geometry has been added!"
        tools_qgis.show_info(message)
        emit_point.canvasClicked.disconnect()
        global_vars.canvas.xyCoordinates.disconnect()
        global_vars.iface.mapCanvas().refreshAllLayers()
        vertex_marker.hide()