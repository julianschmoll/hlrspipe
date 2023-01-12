from pathlib import Path

from PySide2.QtWidgets import *
import shiboken2
import maya.OpenMayaUI as omui
import pymel.core as pc

import hlrsutil

version = 2.1


def get_maya_win():
    ptr = omui.MQtUtil().mainWindow()
    return shiboken2.wrapInstance(int(ptr), QWidget)


class HlrsWin(QMainWindow):
    def __init__(self):
        super().__init__(parent=get_maya_win())
        self.folder = None
        self._create_widgets()
        self._connect_widgets()
        self._create_layout()
        self.show()

    def _create_widgets(self):
        self.dir_lineedit = QLineEdit()
        self.dir_lineedit.setEnabled(False)
        self.dir_lineedit.setText("Choose file directory")
        self.choose_btn = QPushButton("")
        pixmap = QStyle.SP_DirIcon
        icon = self.style().standardIcon(pixmap)
        self.choose_btn.setIcon(icon)
        self.resource_folder_text = QLabel()
        self.resource_folder_text.setText("Resource folder name:")

        filename = pc.sceneName().name
        parts = str(filename).split("_")
        
        self.explain_text = QLabel()
        self.explain_text.setText(f"This tool exports current shot to the selected folder:")

        rs = pc.PyNode("defaultRenderGlobals")
        startframe = rs.getAttr("startFrame")
        endframe = rs.getAttr("endFrame")
        cameras = pc.ls(type = 'camera')
        for camera in cameras:
            if camera.getAttr("renderable"):
                rendercam = camera

        self.explain_arnold_text = QLabel()
        self.explain_arnold_text.setText(f"Framerange: {startframe} to {endframe}. Active camera: {rendercam}")

        render_layers = pc.ls(type='renderLayer')

        # Extract the names of the render layers
        self.render_layer_names = [rl.name() for rl in render_layers]
       
        self.render_layer_lineedit = QLineEdit()
        self.render_layer_lineedit.setText(f"{self.render_layer_names}")
                
        self.scene_name_text = QLabel()
        self.scene_name_text.setText("Scene Name:")

        self.scene_name_lineedit = QLineEdit()
        self.scene_name_lineedit.setText("StuProPanda/testcube_v05")
        
        self.resource_folder_lineedit = QLineEdit()
        self.resource_folder_lineedit.setText("panda/resources")
        
        self.ok_btn = QPushButton("Export selected layers")
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    def _connect_widgets(self):
        self.ok_btn.clicked.connect(self._copy_files)
        self.choose_btn.clicked.connect(self._get_dir)

    def _create_layout(self):
        vbox = QVBoxLayout()
        
        vbox.addWidget(self.explain_text)

        dir_hbox = QHBoxLayout()
        dir_hbox.addWidget(self.dir_lineedit, stretch=1)
        dir_hbox.addWidget(self.choose_btn)
        vbox.addLayout(dir_hbox)

        res_hbox = QHBoxLayout()
        res_hbox.addWidget(self.resource_folder_text)
        res_hbox.addWidget(self.resource_folder_lineedit, stretch = 1)
        vbox.addLayout(res_hbox)
        
        sname_hbox = QHBoxLayout()
        sname_hbox.addWidget(self.scene_name_text)
        sname_hbox.addWidget(self.scene_name_lineedit, stretch = 1)
        vbox.addLayout(sname_hbox)

        vbox.addWidget(self.explain_arnold_text)
        
        self.checkboxes = []

        # Extract the names of the render layers
        objs = self.render_layer_names
        for name in objs:
            checkbox = QCheckBox(name)
            self.checkboxes.append(checkbox)
            vbox.addWidget(checkbox)
        
        vbox.addWidget(self.ok_btn)
        
        central_widget = QWidget()
        central_widget.setLayout(vbox)
        
        self.setWindowTitle(f"HLRS Export v{version}")
        self.setCentralWidget(central_widget)

    def _copy_files(self):
        resources = self.resource_folder_lineedit.text() or "resources"
        filename = pc.sceneName().name
        self.folder = self.dir_lineedit.text()
        
        resource_folder = Path(self.folder) / resources
        resource_folder.mkdir(parents=True, exist_ok=True)
        folders = hlrsutil.collect_files(resource_folder)
        hlrsutil.write_pathmap(folders, resources, Path(self.folder))
        scene_name = Path(self.folder) / pc.sceneName().name

        rs = pc.PyNode("defaultRenderGlobals")
        startframe = rs.getAttr("startFrame")
        endframe = rs.getAttr("endFrame")
        self.statusBar.showMessage("Succesfully exported Files",2000)
        
        for checkbox in self.checkboxes:
            if checkbox.isChecked():
                print(f"# Exporting {checkbox.text()}...")
                pc.editRenderLayerGlobals( currentRenderLayer=checkbox.text())
                pc.other.arnoldExportAss(f=f"{scene_name}_<RenderLayer>.ass", startFrame = startframe, endFrame = endframe, preserveReferences=True)
                print(f"Succesfully exported {checkbox.text()}")
                for x in range(int(startframe), int(endframe)):
                    if f"{checkbox.text()}" == "defaultRenderLayer":
                        text = "masterLayer"
                    else:
                        text = checkbox.text()
                    number = "%04d" % (x,)
                    
                    SEQUENZ_NAME = self.scene_name_lineedit.text()
                    ASS_ROOT_DIR_NAME=SEQUENZ_NAME
                    WORKSPACE_DIR_NAME="/zhome/academic/HLRS/zmc/zmcbeber/Arnold_SDK-7.1.3.1_Linux/Job_dir"
                    ARNOLD_ROOT_PATH="/zhome/academic/HLRS/zmc/zmcbeber/Arnold_SDK-7.1.3.1_Linux"
                    ACES_PATH="/lustre/hpe/ws10/ws10.1/ws/zmcbeber-workspace1/zmcbeber-workspace1/ocio/aces_1.2"
    
                    hlrsutil.write_job_file(Path(self.folder), f"{scene_name}_{text}.{number}", SEQUENZ_NAME, WORKSPACE_DIR_NAME, ASS_ROOT_DIR_NAME, ARNOLD_ROOT_PATH, ACES_PATH)
      
        self.statusBar.showMessage("Succesfully exported ASS Files",2000)
        print("Succesfully exported ASS Files")
        self.close()

    def _get_dir(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Choose Directory",
            str(pc.Workspace().path),
            QFileDialog.ShowDirsOnly
        )
        self.dir_lineedit.setText(folder)