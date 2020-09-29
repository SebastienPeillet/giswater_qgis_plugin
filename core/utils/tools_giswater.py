"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import QTabWidget
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QCursor, QPixmap
from qgis.core import QgsProject, QgsExpression

import configparser
import global_vars
import os
import sys
if 'nt' in sys.builtin_module_names:
    import ctypes

from lib import tools_qt
from core.ui.ui_manager import GwDialog, GwMainWindow


def load_settings(dialog):
    """ Load user UI settings related with dialog position and size """
    # Get user UI config file
    try:
        x = get_parser_value('dialogs_position', f"{dialog.objectName()}_x")
        y = get_parser_value('dialogs_position', f"{dialog.objectName()}_y")
        width = get_parser_value('dialogs_position', f"{dialog.objectName()}_width")
        height = get_parser_value('dialogs_position', f"{dialog.objectName()}_height")

        v_screens = ctypes.windll.user32
        screen_x = v_screens.GetSystemMetrics(78)  # Width of virtual screen
        screen_y = v_screens.GetSystemMetrics(79)  # Height of virtual screen
        monitors = v_screens.GetSystemMetrics(80)  # Will return an integer of the number of display monitors present.

        if (int(x) < 0 and monitors == 1) or (int(y) < 0 and monitors == 1):
            dialog.resize(int(width), int(height))
        else:
            if int(x) > screen_x:
                x = int(screen_x) - int(width)
            if int(y) > screen_y:
                y = int(screen_y)
            dialog.setGeometry(int(x), int(y), int(width), int(height))
    except:
        pass


def save_settings(dialog):
    """ Save user UI related with dialog position and size """
    try:
        set_parser_value('dialogs_position', f"{dialog.objectName()}_width", f"{dialog.property('width')}")
        set_parser_value('dialogs_position', f"{dialog.objectName()}_height", f"{dialog.property('height')}")
        set_parser_value('dialogs_position', f"{dialog.objectName()}_x", f"{dialog.pos().x() + 8}")
        set_parser_value('dialogs_position', f"{dialog.objectName()}_y", f"{dialog.pos().y() + 31}")
    except Exception as e:
        pass


def get_parser_value(section: str, parameter: str) -> str:
    """ Load a simple parser value """
    value = None
    try:
        parser = configparser.ConfigParser(comment_prefixes=';', allow_no_value=True)
        main_folder = os.path.join(os.path.expanduser("~"), global_vars.plugin_name)
        path = main_folder + os.sep + "config" + os.sep + 'user.config'
        if not os.path.exists(path):
            return value
        parser.read(path)
        value = parser[section][parameter]
    except:
        return value
    return value


def set_parser_value(section: str, parameter: str, value: str):
    """  Save simple parser value """
    try:
        parser = configparser.ConfigParser(comment_prefixes=';', allow_no_value=True)
        main_folder = os.path.join(os.path.expanduser("~"), global_vars.plugin_name)
        config_folder = main_folder + os.sep + "config" + os.sep
        if not os.path.exists(config_folder):
            os.makedirs(config_folder)
        path = config_folder + 'user.config'
        parser.read(path)

        # Check if section dialogs_position exists in file
        if section not in parser:
            parser.add_section(section)
        parser[section][parameter] = value
        with open(path, 'w') as configfile:
            parser.write(configfile)
            configfile.close()
    except Exception as e:
        return None


def save_current_tab(dialog, tab_widget, selector_name):
    """ Save the name of current tab used by the user into QSettings()
    :param dialog: QDialog
    :param tab_widget:  QTabWidget
    :param selector_name: Name of the selector (String)
    """
    try:
        index = tab_widget.currentIndex()
        tab = tab_widget.widget(index)
        if tab:
            tab_name = tab.objectName()
            dlg_name = dialog.objectName()
            set_parser_value('last_tabs', f"{dlg_name}_{selector_name}", f"{tab_name}")

    except Exception as e:
        pass


def open_dialog(dlg, dlg_name=None, info=True, maximize_button=True, stay_on_top=True, title=None):
    """ Open dialog """

    # Check database connection before opening dialog
    if not global_vars.controller.check_db_connection():
        return

    # Set window title
    if title is not None:
        dlg.setWindowTitle(title)
    else:
        if dlg_name:
            global_vars.controller.manage_translation(dlg_name, dlg)

    # Manage stay on top, maximize/minimize button and information button
    # if info is True maximize flag will be ignored
    # To enable maximize button you must set info to False
    flags = Qt.WindowCloseButtonHint
    if info:
        flags |= Qt.WindowSystemMenuHint | Qt.WindowContextHelpButtonHint
    else:
        if maximize_button:
            flags |= Qt.WindowMinMaxButtonsHint

    if stay_on_top:
        flags |= Qt.WindowStaysOnTopHint

    dlg.setWindowFlags(flags)

    # Open dialog
    if issubclass(type(dlg), GwDialog):
        dlg.open()
    elif issubclass(type(dlg), GwMainWindow):
        dlg.show()
    else:
        dlg.show()


def close_dialog(dlg):
    """ Close dialog """

    try:
        save_settings(dlg)
        dlg.close()
        map_tool = global_vars.canvas.mapTool()
        # If selected map tool is from the plugin, set 'Pan' as current one
        if map_tool.toolName() == '':
            global_vars.iface.actionPan().trigger()
    except AttributeError:
        pass

    global_vars.schema = None


def create_body(form='', feature='', filter_fields='', extras=None):
    """ Create and return parameters as body to functions"""

    client = f'$${{"client":{{"device":4, "infoType":1, "lang":"ES"}}, '
    form = f'"form":{{{form}}}, '
    feature = f'"feature":{{{feature}}}, '
    filter_fields = f'"filterFields":{{{filter_fields}}}'
    page_info = f'"pageInfo":{{}}'
    data = f'"data":{{{filter_fields}, {page_info}'
    if extras is not None:
        data += ', ' + extras
    data += f'}}}}$$'
    body = "" + client + form + feature + data

    return body


# Currently in parent_maptool
# def set_action_pan(controller):
# 	""" Set action 'Pan' """
# 	try:
# 		controller.iface.actionPan().trigger()
# 	except Exception:
# 		pass


def populate_info_text(dialog, data, force_tab=True, reset_text=True, tab_idx=1):

    change_tab = False
    text = tools_qt.getWidgetText(dialog, 'txt_infolog', return_string_null=False)
    if reset_text:
        text = ""
    for item in data['info']['values']:
        if 'message' in item:
            if item['message'] is not None:
                text += str(item['message']) + "\n"
                if force_tab:
                    change_tab = True
            else:
                text += "\n"

    tools_qt.setWidgetText(dialog, 'txt_infolog', text + "\n")
    qtabwidget = dialog.findChild(QTabWidget, 'mainTab')
    if change_tab and qtabwidget is not None:
        qtabwidget.setCurrentIndex(tab_idx)

    return change_tab


def refresh_legend(controller):
    """ This function solves the bug generated by changing the type of feature.
    Mysteriously this bug is solved by checking and unchecking the categorization of the tables.
    # TODO solve this bug
    """
    layers = [controller.get_layer_by_tablename('v_edit_node'),
              controller.get_layer_by_tablename('v_edit_connec'),
              controller.get_layer_by_tablename('v_edit_gully')]

    for layer in layers:
        if layer:
            ltl = QgsProject.instance().layerTreeRoot().findLayer(layer.id())
            ltm = controller.iface.layerTreeView().model()
            legendNodes = ltm.layerLegendNodes(ltl)
            for ln in legendNodes:
                current_state = ln.data(Qt.CheckStateRole)
                ln.setData(Qt.Unchecked, Qt.CheckStateRole)
                ln.setData(Qt.Checked, Qt.CheckStateRole)
                ln.setData(current_state, Qt.CheckStateRole)


def check_expression(expr_filter, log_info=False):
    """ Check if expression filter @expr is valid """

    if log_info:
        global_vars.controller.log_info(expr_filter)
    expr = QgsExpression(expr_filter)
    if expr.hasParserError():
        message = "Expression Error"
        global_vars.controller.log_warning(message, parameter=expr_filter)
        return False, expr

    return True, expr


def get_cursor_multiple_selection():
    """ Set cursor for multiple selection """

    path_folder = os.path.join(os.path.dirname(__file__), os.pardir)
    path_cursor = os.path.join(path_folder, 'icons', '201.png')

    print(path_folder)
    print(path_cursor)

    if os.path.exists(path_cursor):
        cursor = QCursor(QPixmap(path_cursor))
    else:
        cursor = QCursor(Qt.ArrowCursor)

    return cursor


def hide_generic_layers(excluded_layers=[]):
    """ Hide generic layers """

    layer = global_vars.controller.get_layer_by_tablename("v_edit_arc")
    if layer and "v_edit_arc" not in excluded_layers:
        global_vars.controller.set_layer_visible(layer)
    layer = global_vars.controller.get_layer_by_tablename("v_edit_node")
    if layer and "v_edit_node" not in excluded_layers:
        global_vars.controller.set_layer_visible(layer)
    layer = global_vars.controller.get_layer_by_tablename("v_edit_connec")
    if layer and "v_edit_connec" not in excluded_layers:
        global_vars.controller.set_layer_visible(layer)
    layer = global_vars.controller.get_layer_by_tablename("v_edit_element")
    if layer and "v_edit_element" not in excluded_layers:
        global_vars.controller.set_layer_visible(layer)

    if global_vars.project_type == 'ud':
        layer = global_vars.controller.get_layer_by_tablename("v_edit_gully")
        if layer and "v_edit_gully" not in excluded_layers:
            global_vars.controller.set_layer_visible(layer)


def get_plugin_version():
    """ Get plugin version from metadata.txt file """

    # Check if metadata file exists
    metadata_file = os.path.join(global_vars.plugin_dir, 'metadata.txt')
    if not os.path.exists(metadata_file):
        message = "Metadata file not found"
        global_vars.controller.show_warning(message, parameter=metadata_file)
        return None

    metadata = configparser.ConfigParser()
    metadata.read(metadata_file)
    plugin_version = metadata.get('general', 'version')
    if plugin_version is None:
        message = "Plugin version not found"
        global_vars.controller.show_warning(message)

    return plugin_version


def manage_actions(json_result, sql):
    """
    Manage options for layers (active, visible, zoom and indexing)
    :param json_result: Json result of a query (Json)
    :return: None
    """

    try:
        actions = json_result['body']['python_actions']
    except KeyError:
        return
    try:
        for action in actions:
            try:
                function_name = action['funcName']
                params = action['params']
                getattr(global_vars.controller.gw_infotools, f"{function_name}")(**params)
            except AttributeError as e:
                # If function_name not exist as python function
                global_vars.controller.log_warning(f"Exception error: {e}")
            except Exception as e:
                global_vars.controller.log_debug(f"{type(e).__name__}: {e}")
    except Exception as e:
        global_vars.controller.manage_exception(None, f"{type(e).__name__}: {e}", sql)


def draw(complet_result, rubber_band, margin=None, reset_rb=True, color=QColor(255, 0, 0, 100), width=3):

    try:
        if complet_result['body']['feature']['geometry'] is None:
            return
        if complet_result['body']['feature']['geometry']['st_astext'] is None:
            return
    except KeyError:
        return

    list_coord = re.search('\((.*)\)', str(complet_result['body']['feature']['geometry']['st_astext']))
    max_x, max_y, min_x, min_y = get_max_rectangle_from_coords(list_coord)

    if reset_rb:
        rubber_band.reset()
    if str(max_x) == str(min_x) and str(max_y) == str(min_y):
        point = QgsPointXY(float(max_x), float(max_y))
        draw_point(point, rubber_band, color, width)
    else:
        points = get_points(list_coord)
        draw_polyline(points, rubber_band, color, width)
    if margin is not None:
        zoom_to_rectangle(max_x, max_y, min_x, min_y, margin)


def draw_point(point, rubber_band=None, color=QColor(255, 0, 0, 100), width=3, duration_time=None, is_new=False):
    """
    :param duration_time: integer milliseconds ex: 3000 for 3 seconds
    """

    rubber_band.reset(0)
    rubber_band.setIconSize(10)
    rubber_band.setColor(color)
    rubber_band.setWidth(width)
    rubber_band.addPoint(point)

    # wait to simulate a flashing effect
    if duration_time is not None:
        QTimer.singleShot(duration_time, rubber_band.reset)


def draw_polyline(points, rubber_band, color=QColor(255, 0, 0, 100), width=5, duration_time=None):
    """ Draw 'line' over canvas following list of points
     :param duration_time: integer milliseconds ex: 3000 for 3 seconds
     """

    rubber_band.setIconSize(20)
    polyline = QgsGeometry.fromPolylineXY(points)
    rubber_band.setToGeometry(polyline, None)
    rubber_band.setColor(color)
    rubber_band.setWidth(width)
    rubber_band.show()

    # wait to simulate a flashing effect
    if duration_time is not None:
        QTimer.singleShot(duration_time, rubber_band.reset)



def enable_feature_type(dialog, widget_name='tbl_relation', ids=None):

    feature_type = tools_qt.getWidget(dialog, 'feature_type')
    widget_table = tools_qt.getWidget(dialog, widget_name)
    if feature_type is not None and widget_table is not None:
        if len(ids) > 0:
            feature_type.setEnabled(False)
        else:
            feature_type.setEnabled(True)




# Doesn't work because of hasattr and getattr
'''



def set_selector(dialog, widget, is_alone, controller):
	"""  Send values to DB and reload selectors
	:param dialog: QDialog
	:param widget: QCheckBox that contains the information to generate the json (QCheckBox)
	:param is_alone: Defines if the selector is unique (True) or multiple (False) (Boolean)
	"""
	
	# Get current tab name
	index = dialog.main_tab.currentIndex()
	tab_name = dialog.main_tab.widget(index).objectName()
	selector_type = dialog.main_tab.widget(index).property("selector_type")
	qgis_project_add_schema = controller.plugin_settings_value('gwAddSchema')
	widget_all = dialog.findChild(QCheckBox, f'chk_all_{tab_name}')
	
	if widget_all is None or (widget_all is not None and widget.objectName() != widget_all.objectName()):
		extras = (f'"selectorType":"{selector_type}", "tabName":"{tab_name}", '
				  f'"id":"{widget.objectName()}", "isAlone":"{is_alone}", "value":"{widget.isChecked()}", '
				  f'"addSchema":"{qgis_project_add_schema}"')
	else:
		check_all = qt_tools.isChecked(dialog, widget_all)
		extras = f'"selectorType":"{selector_type}", "tabName":"{tab_name}", "checkAll":"{check_all}",  ' \
				 f'"addSchema":"{qgis_project_add_schema}"'
	
	body = create_body(extras=extras)
	json_result = controller.get_json('gw_fct_setselectors', body)
	
	if str(tab_name) == 'tab_exploitation':
		# Reload layer, zoom to layer, style mapzones and refresh canvas
		layer = controller.get_layer_by_tablename('v_edit_arc')
		if layer:
			self.iface.setActiveLayer(layer)
			self.iface.zoomToActiveLayer()
		self.set_style_mapzones()
	
	# Refresh canvas
	controller.set_layer_index('v_edit_arc')
	controller.set_layer_index('v_edit_node')
	controller.set_layer_index('v_edit_connec')
	controller.set_layer_index('v_edit_gully')
	controller.set_layer_index('v_edit_link')
	controller.set_layer_index('v_edit_plan_psector')
	
	get_selector(dialog, f'"{selector_type}"', controller, is_setselector=json_result)
	
	widget_filter = qt_tools.getWidget(dialog, f"txt_filter_{tab_name}")
	if widget_filter and qt_tools.getWidgetText(dialog, widget_filter, False, False) not in (None, ''):
		widget_filter.textChanged.emit(widget_filter.text())


def manage_all(dialog, widget_all, controller):
	
	key_modifier = QApplication.keyboardModifiers()
	status = qt_tools.isChecked(dialog, widget_all)
	index = dialog.main_tab.currentIndex()
	widget_list = dialog.main_tab.widget(index).findChildren(QCheckBox)
	if key_modifier == Qt.ShiftModifier:
		return
	
	for widget in widget_list:
		if widget_all is not None:
			if widget == widget_all or widget.objectName() == widget_all.objectName():
				continue
		widget.blockSignals(True)
		qt_tools.setChecked(dialog, widget, status)
		widget.blockSignals(False)
	
	set_selector(dialog, widget_all, False, controller)


def get_selector(dialog, selector_type, controller, filter=False, widget=None, text_filter=None, current_tab=None,
				 is_setselector=None):
	""" Ask to DB for selectors and make dialog
	:param dialog: Is a standard dialog, from file api_selectors.ui, where put widgets
	:param selector_type: list of selectors to ask DB ['exploitation', 'state', ...]
	"""
	main_tab = dialog.findChild(QTabWidget, 'main_tab')
	
	# Set filter
	if filter is not False:
		main_tab = dialog.findChild(QTabWidget, 'main_tab')
		text_filter = qt_tools.getWidgetText(dialog, widget)
		if text_filter in ('null', None):
			text_filter = ''
		
		# Set current_tab
		index = dialog.main_tab.currentIndex()
		current_tab = dialog.main_tab.widget(index).objectName()
	
	# Profilactic control of nones
	if text_filter is None:
		text_filter = ''
	if is_setselector is None:
		# Built querytext
		form = f'"currentTab":"{current_tab}"'
		extras = f'"selectorType":{selector_type}, "filterText":"{text_filter}"'
		body = create_body(form=form, extras=extras)
		json_result = controller.get_json('gw_fct_getselectors', body)
	else:
		json_result = is_setselector
		for x in range(dialog.main_tab.count() - 1, -1, -1):
			dialog.main_tab.widget(x).deleteLater()
	
	if not json_result:
		return False
	
	for form_tab in json_result['body']['form']['formTabs']:
		
		if filter and form_tab['tabName'] != str(current_tab):
			continue
		
		selection_mode = form_tab['selectionMode']
		
		# Create one tab for each form_tab and add to QTabWidget
		tab_widget = QWidget(main_tab)
		tab_widget.setObjectName(form_tab['tabName'])
		tab_widget.setProperty('selector_type', form_tab['selectorType'])
		if filter:
			main_tab.removeTab(index)
			main_tab.insertTab(index, tab_widget, form_tab['tabLabel'])
		else:
			main_tab.addTab(tab_widget, form_tab['tabLabel'])
		
		# Create a new QGridLayout and put it into tab
		gridlayout = QGridLayout()
		gridlayout.setObjectName("grl_" + form_tab['tabName'])
		tab_widget.setLayout(gridlayout)
		field = {}
		i = 0
		
		if 'typeaheadFilter' in form_tab:
			label = QLabel()
			label.setObjectName('lbl_filter')
			label.setText('Filter:')
			if qt_tools.getWidget(dialog, 'txt_filter_' + str(form_tab['tabName'])) is None:
				widget = QLineEdit()
				widget.setObjectName('txt_filter_' + str(form_tab['tabName']))
				widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
				widget.textChanged.connect(partial(get_selector, dialog, selector_type, filter=True,
												   widget=widget, current_tab=current_tab))
				widget.textChanged.connect(partial(self.manage_filter, dialog, widget, 'save'))
				widget.setLayoutDirection(Qt.RightToLeft)
				setattr(self, f"var_txt_filter_{form_tab['tabName']}", '')
			else:
				widget = qt_tools.getWidget(dialog, 'txt_filter_' + str(form_tab['tabName']))
			
			field['layoutname'] = gridlayout.objectName()
			field['layoutorder'] = i
			i = i + 1
			self.put_widgets(dialog, field, label, widget)
			widget.setFocus()
		
		if 'manageAll' in form_tab:
			if (form_tab['manageAll']).lower() == 'true':
				if qt_tools.getWidget(dialog, f"lbl_manage_all_{form_tab['tabName']}") is None:
					label = QLabel()
					label.setObjectName(f"lbl_manage_all_{form_tab['tabName']}")
					label.setText('Check all')
				else:
					label = qt_tools.getWidget(dialog, f"lbl_manage_all_{form_tab['tabName']}")
				
				if qt_tools.getWidget(dialog, f"chk_all_{form_tab['tabName']}") is None:
					widget = QCheckBox()
					widget.setObjectName('chk_all_' + str(form_tab['tabName']))
					widget.stateChanged.connect(partial(self.manage_all, dialog, widget))
					widget.setLayoutDirection(Qt.RightToLeft)
				
				else:
					widget = qt_tools.getWidget(dialog, f"chk_all_{form_tab['tabName']}")
				field['layoutname'] = gridlayout.objectName()
				field['layoutorder'] = i
				i = i + 1
				chk_all = widget
				self.put_widgets(dialog, field, label, widget)
		
		for order, field in enumerate(form_tab['fields']):
			label = QLabel()
			label.setObjectName('lbl_' + field['label'])
			label.setText(field['label'])
			
			widget = self.add_checkbox(field)
			widget.stateChanged.connect(partial(self.set_selection_mode, dialog, widget, selection_mode))
			widget.setLayoutDirection(Qt.RightToLeft)
			
			field['layoutname'] = gridlayout.objectName()
			field['layoutorder'] = order + i
			self.put_widgets(dialog, field, label, widget)
		
		vertical_spacer1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
		gridlayout.addItem(vertical_spacer1)
	
	# Set last tab used by user as current tab
	tabname = json_result['body']['form']['currentTab']
	tab = main_tab.findChild(QWidget, tabname)
	
	if tab:
		main_tab.setCurrentWidget(tab)
	
	if is_setselector is not None and hasattr(self, 'widget_filter'):
		widget = dialog.main_tab.findChild(QLineEdit, f'txt_filter_{tabname}')
		if widget:
			widget.blockSignals(True)
			index = dialog.main_tab.currentIndex()
			tab_name = dialog.main_tab.widget(index).objectName()
			value = getattr(self, f"var_txt_filter_{tab_name}")
			qt_tools.setWidgetText(dialog, widget, f'{value}')
			widget.blockSignals(False)


def manage_filter(dialog, widget, action):
	index = dialog.main_tab.currentIndex()
	tab_name = dialog.main_tab.widget(index).objectName()
	if action == 'save':
		setattr(self, f"var_txt_filter_{tab_name}", qt_tools.getWidgetText(dialog, widget))
	else:
		setattr(self, f"var_txt_filter_{tab_name}", '')

'''''
