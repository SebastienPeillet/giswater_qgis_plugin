"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
from qgis.PyQt import uic, QtCore
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMainWindow, QDialog, QDockWidget, QWhatsThis, QLineEdit
import configparser
import os
import webbrowser


class GwDockWidget(QDockWidget):

    dlg_closed = QtCore.pyqtSignal()
    
    def __init__(self, subtag=None, position=None):
        super().__init__()
        self.setupUi(self)
        self.subtag = subtag


    def closeEvent(self, event):
        self.dlg_closed.emit()
        return super().closeEvent(event)


class GwDialog(QDialog):

    def __init__(self, subtag=None):
        super().__init__()
        self.setupUi(self)
        self.subtag = subtag
        # Enable event filter
        self.installEventFilter(self)


    def eventFilter(self, object, event):

        if event.type() == QtCore.QEvent.EnterWhatsThisMode and self.isActiveWindow():
            QWhatsThis.leaveWhatsThisMode()
            parser = configparser.ConfigParser()
            path = os.path.dirname(__file__) + '/config/ui_config.config'
            parser.read(path)
            
            if self.subtag is not None:
                tag = f'{self.objectName()}_{self.subtag}'
            else:
                tag = str(self.objectName())

            try:
                web_tag = parser.get('web_tag', tag)
                webbrowser.open_new_tab('https://giswater.org/giswater-manual/#' + web_tag)
            except Exception as e:
                webbrowser.open_new_tab('https://giswater.org/giswater-manual')
            
            return True
        return False


class GwMainWindow(QMainWindow):

    dlg_closed = QtCore.pyqtSignal()
    
    def __init__(self, subtag=None):
        super().__init__()
        self.setupUi(self)
        self.subtag = subtag
        # Enable event filter
        self.installEventFilter(self)


    def closeEvent(self, event):
        self.dlg_closed.emit()
        try:
            return super().closeEvent(event)
        except RuntimeError:
            pass



    def eventFilter(self, object, event):

        if event.type() == QtCore.QEvent.EnterWhatsThisMode and self.isActiveWindow():
            QWhatsThis.leaveWhatsThisMode()
            parser = configparser.ConfigParser()
            path = os.path.dirname(__file__) + '/config/ui_config.config'
            parser.read(path)
        
            if self.subtag is not None:
                tag = f'{self.objectName()}_{self.subtag}'
            else:
                tag = str(self.objectName())
                
            try:
                web_tag = parser.get('web_tag', tag)
                webbrowser.open_new_tab('https://giswater.org/giswater-manual/#' + web_tag)
            except Exception as e:
                webbrowser.open_new_tab('https://giswater.org/giswater-manual')

            return True
        return False


def get_ui_class(ui_file_name, subfolder=None):
    """ Get UI Python class from @ui_file_name """

    # Folder that contains UI files
    ui_folder_path = os.path.dirname(__file__) + os.sep + 'ui'
    if subfolder:
        ui_folder_path += os.sep + subfolder
    ui_file_path = os.path.abspath(os.path.join(ui_folder_path, ui_file_name))
    return uic.loadUiType(ui_file_path)[0]


FORM_CLASS = get_ui_class('docker.ui')
class DockerUi(GwDockWidget, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('element.ui')
class ElementUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('visit.ui')
class VisitUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('info_generic.ui')
class InfoGenericUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('info_catalog.ui')
class InfoCatalogUi(GwMainWindow, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('info_feature.ui')
class InfoFeatureUi(GwMainWindow, FORM_CLASS):
    key_escape = QtCore.pyqtSignal()
    key_enter = QtCore.pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.key_escape.emit()
            return super(InfoFeatureUi, self).keyPressEvent(event)
        elif event.key() == QtCore.Qt.Key_Enter:
            self.key_enter.emit()
            return super(InfoFeatureUi, self).keyPressEvent(event)


FORM_CLASS = get_ui_class('fastprint.ui')
class FastPrintUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('config.ui')
class ConfigUi(GwMainWindow, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('dimensioning.ui')
class DimensioningUi(GwMainWindow, FORM_CLASS):
    key_escape = QtCore.pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.key_escape.emit()
            return super(DimensioningUi, self).keyPressEvent(event)


FORM_CLASS = get_ui_class('go2epa_options.ui')
class Go2EpaOptionsUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('search.ui')
class SearchUi(GwDockWidget, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('selector.ui')
class SelectorUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('toolbox_docker.ui')
class ToolboxDockerUi(GwDockWidget, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('toolbox.ui')
class ToolboxUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('arc_fusion.ui')
class ArcFusionUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('project_check.ui')
class ProjectCheckUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('dialog_text.ui')
class DialogTextUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('dialog_table.ui')
class BasicTable(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('auxcircle.ui')
class AuxCircle(GwDialog, FORM_CLASS):
    pass
        

FORM_CLASS = get_ui_class('auxpoint.ui')
class AuxPoint(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('nodetype_change.ui')
class NodeTypeChange(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('main_credentials.ui')
class Credentials(GwDialog, FORM_CLASS):

    def __init__(self, subtag=None):

        super().__init__()
        self.txt_pass.setClearButtonEnabled(True)
        icon_path = os.path.dirname(__file__) + os.sep + 'icons' + os.sep + 'eye_open.png'
        self.action = QAction("show")
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            self.action = QAction(icon, "show")
        self.action.triggered.connect(self.show_pass)
        self.txt_pass.addAction(self.action, QLineEdit.TrailingPosition)


    def show_pass(self):

        icon_path = ""
        text = ""
        if self.txt_pass.echoMode() == 0:
            self.txt_pass.setEchoMode(QLineEdit.Password)
            icon_path = os.path.dirname(__file__) + os.sep + 'icons' + os.sep + 'eye_open.png'
            text = "Show password"
        elif self.txt_pass.echoMode() == 2:
            self.txt_pass.setEchoMode(QLineEdit.Normal)
            icon_path = os.path.dirname(__file__) + os.sep + 'icons' + os.sep + 'eye_close.png'
            text = "Hide password"
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            self.action.setIcon(icon)
            self.action.setText(text)


FORM_CLASS = get_ui_class('crm_trace.ui')
class DlgTrace(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('csv.ui')
class CsvUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('feature_delete.ui')
class FeatureDelete(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('doc.ui')
class DocUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('doc_manager.ui')
class DocManager(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('profile.ui')
class Profile(GwMainWindow, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('psector_duplicate.ui')
class PsectorDuplicate(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('element_manager.ui')
class ElementManager(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('go2epa_selector.ui')
class Go2EpaSelectorUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('go2epa_manager.ui')
class EpaManager(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('visit_event_full.ui')
class VisitEventFull(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('visit_event_rehab.ui')
class VisitEventRehab(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('visit_event.ui')
class VisitEvent(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('go2epa.ui')
class Go2EpaUI(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('visit_gallery.ui')
class Gallery(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('visit_gallery_zoom.ui')
class GalleryZoom(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('hydrology_selector.ui')
class HydrologySelector(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('info_show_info.ui')
class InfoShowInfo(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('search_workcat.ui')
class SearchWorkcat(GwDialog, FORM_CLASS):
    pass

FORM_CLASS = get_ui_class('visit_document.ui')
class VisitDocument(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('profile_list.ui')
class ProfilesList(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('main_addfields.ui')
class MainFields(GwDialog, FORM_CLASS):
    pass

FORM_CLASS = get_ui_class('main_sysfields.ui')
class MainSysFields(GwDialog, FORM_CLASS):
    pass

FORM_CLASS = get_ui_class('main_visitclass.ui')
class MainVisitClass(GwDialog, FORM_CLASS):
    pass

FORM_CLASS = get_ui_class('main_visitparam.ui')
class MainVisitParam(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('mincut.ui')
class Mincut(GwMainWindow, FORM_CLASS):

    def __init__(self):
        self.closeMainWin = False
        self.mincutCanceled = True
        super().__init__()


FORM_CLASS = get_ui_class('mincut_connec.ui')
class MincutConnec(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('mincut_hydrometer.ui')
class MincutHydrometer(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('mincut_composer.ui')
class MincutComposer(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('mincut_manager.ui')
class MincutManagerUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('mincut_end.ui')
class MincutEndUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('multirow_selector.ui')
class Multirow_selector(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('info_workcat.ui')
class InfoWorkcatUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('feature_replace.ui')
class FeatureReplace(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('price_manager.ui')
class PriceManagerUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('plan_psector.ui')
class Plan_psector(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('psector_manager.ui')
class PsectorManagerUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('psector_rapport.ui')
class PsectorRapportUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('main_qtdialog.ui')
class MainQtDialogUi(GwDialog, FORM_CLASS):

    def __init__(self, subtag=None):

        super().__init__()
        self.txt_pass.setClearButtonEnabled(True)
        icon_path = os.path.dirname(__file__) + os.sep + 'icons' + os.sep + 'eye_open.png'
        self.action = QAction("show")
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            self.action = QAction(icon, "show")
        self.action.triggered.connect(self.show_pass)
        self.txt_pass.addAction(self.action, QLineEdit.TrailingPosition)


    def show_pass(self):

        icon_path = ""
        text = ""
        if self.txt_pass.echoMode() == 0:
            self.txt_pass.setEchoMode(QLineEdit.Password)
            icon_path = os.path.dirname(__file__) + os.sep + 'icons' + os.sep + 'eye_open.png'
            text = "Show password"
        elif self.txt_pass.echoMode() == 2:
            self.txt_pass.setEchoMode(QLineEdit.Normal)
            icon_path = os.path.dirname(__file__) + os.sep + 'icons' + os.sep + 'eye_close.png'
            text = "Hide password"
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            self.action.setIcon(icon)
            self.action.setText(text)


FORM_CLASS = get_ui_class('main_ui.ui')
class MainUi(GwMainWindow, FORM_CLASS):
    dlg_closed = QtCore.pyqtSignal()
    pass


FORM_CLASS = get_ui_class('main_dbproject.ui')
class MainDbProjectUi(GwMainWindow, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('main_gisproject.ui')
class MainGisProjectUi(GwMainWindow, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('main_renameproj.ui')
class MainRenameProjUi(GwMainWindow, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('main_projectinfo.ui')
class MainProjectInfoUi(GwMainWindow, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('info_crossect.ui')
class InfoCrossectUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('selector_date.ui')
class SelectorDate(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('lot_visitmanager.ui')
class LotVisitManagerUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('feature_end.ui')
class FeatureEndUi(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('feature_end_connec.ui')
class FeatureEndConnecUi(GwDialog, FORM_CLASS):
    pass


""" Tree Manage forms """
FORM_CLASS = get_ui_class('add_visit.ui', 'tm')
class AddVisitTm(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('event_standard.ui', 'tm')
class EventStandardTm(GwDialog, FORM_CLASS):
    pass

FORM_CLASS = get_ui_class('incident_planning.ui', 'tm')
class IncidentPlanning(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('incident_manager.ui', 'tm')
class IncidentManager(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('info_incident.ui', 'tm')
class InfoIncident(GwDialog, FORM_CLASS):
    pass


FORM_CLASS = get_ui_class('planning_unit.ui', 'tm')
class PlaningUnit(GwDialog, FORM_CLASS):
    pass
