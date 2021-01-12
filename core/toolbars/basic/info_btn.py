"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import os
import re
from functools import partial

from qgis.PyQt.QtCore import QPoint, Qt
from qgis.PyQt.QtGui import QColor, QCursor, QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.core import QgsGeometry, QgsMapToPixel, QgsPointXY
from qgis.gui import QgsRubberBand
from ...shared import info
from ...shared.info import GwInfo
from ...toolbars.maptool_button import GwMaptoolButton
from ...utils import tools_gw
from .... import global_vars
from ....lib import tools_qgis


class GwInfoButton(GwMaptoolButton):

    def __init__(self, icon_path, action_name, text, toolbar, action_group):
        super().__init__(icon_path, action_name, text, toolbar, action_group)

        self.rubber_band = QgsRubberBand(global_vars.canvas)
        self.tab_type = None
        # Used when the signal 'signal_activate' is emitted from the info, do not open another form
        self.block_signal = False
        self.previous_info_feature = None
        self.action_name = action_name


    def create_point(self, event):

        x = event.pos().x()
        y = event.pos().y()
        try:
            point = QgsMapToPixel.toMapCoordinates(self.canvas.getCoordinateTransform(), x, y)
        except(TypeError, KeyError):
            self.iface.actionPan().trigger()
            return False

        return point


    def reactivate_map_tool(self):
        """ Reactivate tool """
        self.block_signal = True
        info_action = self.iface.mainWindow().findChild(QAction, self.action_name)
        info_action.trigger()


    def get_layers_from_coordinates(self, point, rb_list, tab_type=None):

        cursor = QCursor()
        x = cursor.pos().x()
        y = cursor.pos().y()
        click_point = QPoint(x + 5, y + 5)

        visible_layers = tools_qgis.get_visible_layers(as_list=True)
        scale_zoom = self.iface.mapCanvas().scale()

        # Get layers under mouse clicked
        extras = f'"pointClickCoords":{{"xcoord":{point.x()}, "ycoord":{point.y()}}}, '
        extras += f'"visibleLayers":{visible_layers}, '
        extras += f'"zoomScale":{scale_zoom} '
        body = tools_gw.create_body(extras=extras)
        json_result = tools_gw.execute_procedure('gw_fct_getlayersfromcoordinates', body, rubber_band=self.rubber_band)
        if not json_result or json_result['status'] == 'Failed':
            return False

        # hide QMenu identify if no feature under mouse
        len_layers = len(json_result['body']['data']['layersNames'])
        if len_layers == 0:
            return False

        self.icon_folder = self.plugin_dir + '/icons/'

        # Right click main QMenu
        main_menu = QMenu()

        # Create one menu for each layer
        for layer in json_result['body']['data']['layersNames']:
            layer_name = tools_qgis.get_layer_by_tablename(layer['layerName'])
            icon_path = self.icon_folder + layer['icon'] + '.png'
            if os.path.exists(str(icon_path)):
                icon = QIcon(icon_path)
                sub_menu = main_menu.addMenu(icon, layer_name.name())
            else:
                sub_menu = main_menu.addMenu(layer_name.name())
            # Create one QAction for each id
            for feature in layer['ids']:
                action = QAction(str(feature['id']), None)
                sub_menu.addAction(action)
                action.triggered.connect(partial(self.get_info_from_selected_id, action, tab_type))
                action.hovered.connect(partial(self.draw_by_action, feature, rb_list))

        main_menu.addSeparator()
        # Identify all
        cont = 0
        for layer in json_result['body']['data']['layersNames']:
            cont += len(layer['ids'])
        action = QAction(f'Identify all ({cont})', None)
        action.hovered.connect(partial(self.identify_all, json_result, rb_list))
        main_menu.addAction(action)
        main_menu.addSeparator()
        main_menu.exec_(click_point)



    def identify_all(self, complet_list, rb_list):

        self.rubber_band.reset()
        for rb in rb_list:
            rb.reset()
        for layer in complet_list['body']['data']['layersNames']:
            for feature in layer['ids']:
                points = []
                list_coord = re.search('\((.*)\)', str(feature['geometry']))
                coords = list_coord.group(1)
                polygon = coords.split(',')
                for i in range(0, len(polygon)):
                    x, y = polygon[i].split(' ')
                    point = QgsPointXY(float(x), float(y))
                    points.append(point)
                rb = QgsRubberBand(self.canvas)
                polyline = QgsGeometry.fromPolylineXY(points)
                rb.setToGeometry(polyline, None)
                rb.setColor(QColor(255, 0, 0, 100))
                rb.setWidth(5)
                rb.show()
                rb_list.append(rb)


    def draw_by_action(self, feature, rb_list, reset_rb=True):
        """ Draw lines based on geometry """

        for rb in rb_list:
            rb.reset()
        if feature['geometry'] is None:
            return

        list_coord = re.search('\((.*)\)', str(feature['geometry']))
        max_x, max_y, min_x, min_y = tools_qgis.get_max_rectangle_from_coords(list_coord)
        if reset_rb is True:
            self.rubber_band.reset()
        if str(max_x) == str(min_x) and str(max_y) == str(min_y):
            point = QgsPointXY(float(max_x), float(max_y))
            tools_qgis.draw_point(point, self.rubber_band)
        else:
            points = tools_qgis.get_geometry_vertex(list_coord)
            tools_qgis.draw_polyline(points, self.rubber_band)


    def get_info_from_selected_id(self, action, tab_type):
        """ Set active selected layer """
        self.rubber_band.reset()
        parent_menu = action.associatedWidgets()[0]
        layer = tools_qgis.get_layer_by_layername(parent_menu.title())
        if layer:
            layer_source = tools_qgis.get_layer_source(layer)
            self.iface.setActiveLayer(layer)
            tools_gw.init_docker()
            info_feature = GwInfo(self.tab_type)
            info_feature.signal_activate.connect(self.reactivate_map_tool)
            info_feature.get_info_from_id(table_name=layer_source['table'], feature_id=action.text(), tab_type=tab_type)
            # Remove previous rubberband when open new docker
            if isinstance(self.previous_info_feature, GwInfo) and global_vars.session_vars['dlg_docker'] is not None:
                self.previous_info_feature.rubber_band.reset()
            self.previous_info_feature = info_feature


    # region QgsMapTools inherited
    """ QgsMapTools inherited event functions """

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Escape:
            for rb in self.rubberband_list:
                rb.reset()
            self.rubber_band.reset()
            self.action.trigger()
            return


    def canvasMoveEvent(self, event):
        pass


    def canvasReleaseEvent(self, event):
        self.get_info(event)


    def get_info(self, event):
        for rb in self.rubberband_list:
            rb.reset()

        if self.block_signal:
            self.block_signal = False
            return

        if event.button() == Qt.LeftButton:

            point = self.create_point(event)
            if point is False:
                return
            tools_gw.init_docker()
            info_feature = GwInfo(self.tab_type)
            info_feature.signal_activate.connect(self.reactivate_map_tool)
            info_feature.get_info_from_coordinates(point, tab_type=self.tab_type)
            # Remove previous rubberband when open new docker
            if isinstance(self.previous_info_feature, GwInfo) and global_vars.session_vars['dlg_docker'] is not None:
                self.previous_info_feature.rubber_band.reset()
            self.previous_info_feature = info_feature

        elif event.button() == Qt.RightButton:
            point = self.create_point(event)
            if point is False:
                return

            self.get_layers_from_coordinates(point, self.rubberband_list, self.tab_type)


    def activate(self):
        if info.is_inserting:
            msg = "You cannot insert more than one feature at the same time, finish editing the previous feature"
            tools_qgis.show_message(msg)
            super().deactivate()
            return

        # Check button
        self.action.setChecked(True)
        # Change map tool cursor
        self.cursor = QCursor()
        self.cursor.setShape(Qt.WhatsThisCursor)
        self.canvas.setCursor(self.cursor)
        self.rubberband_list = []
        self.tab_type = 'data'


    def deactivate(self):
        if hasattr(self, 'rubberband_list'):
            for rb in self.rubberband_list:
                rb.reset()
        if hasattr(self, 'dlg_info_feature'):
            self.rubber_band.reset()

        super().deactivate()

    # endregion





