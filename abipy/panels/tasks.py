""""Panels to interact with the AbiPy tasks."""
import param
import panel as pn
import panel.widgets as pnw

from io import StringIO
from abipy.panels.core import AbipyParameterized, mpl, ply, dfc, depends_on_btn_click
from abipy.panels.nodes import NodeParameterized


class AbinitTaskPanel(NodeParameterized):
    """
    Provides widgets to interact with an AbiPy Task.
    """

    def __init__(self, task, **params):
        NodeParameterized.__init__(self, node=task, **params)
        self.task = task

        #self.structures_btn = pnw.Button(name="Show Structures", button_type='primary')
        #self.structures_io_checkbox = pnw.CheckBoxGroup(
        #    name='Input/Output Structure', value=['output'], options=['input', 'output'], inline=Tru

    def get_inputs_view(self):
        """
        Show the input files of the task: submission script and Abinit input file.
        """
        file = self.task.job_file
        text = file.read() if file.exists else "Cannot find job_file!"
        job_file = pn.pane.Markdown(f"```shell\n{text}\n```")

        json_pane = pn.pane.JSON(self.task.manager.as_dict(),
                                 depth=-1, # full expansion
                                 hover_preview=True,
                                 theme="dark",
                                 sizing_mode="stretch_width",
                                 )

        return pn.Column(
            "## Submission script:",
            job_file,
            pn.layout.Divider(),
            "## Input file:",
            self.html_with_clipboard_btn(self.task.input),
            pn.layout.Divider(),
            "## TaskManager:",
            json_pane,
            sizing_mode="stretch_width",
        )

    def get_errs_view(self):
        """
        Show the error files of the task
        Return None if no error is found so that we don't show this view in the GUI.
        """
        col = pn.Column(sizing_mode="stretch_width"); cext = col.extend

        count = 0
        for fname in ("stderr_file", "mpiabort_file", "qerr_file", "qout_file"):
            file = getattr(self.task, fname)
            if file.exists:
                text = file.read().strip()
                if text:
                    cext([f"## {fname}",
                         pn.pane.Markdown(f"```shell\n{text}\n```"),
                         pn.layout.Divider()
                         ])
                    count += 1

        return col if count > 0 else None

    def get_main_text_outs_view(self):
        """
        Show the main text output files of the task.
        """
        col = pn.Column(sizing_mode="stretch_width")
        ca = col.append; cext = col.extend

        for fname in ("output_file", "log_file"):
            file = getattr(self.task, fname)
            text = file.read() if file.exists else f"{fname} does not exist"
            ace = pnw.Ace(value=text, language='text', readonly=True,
                          sizing_mode='stretch_width', height=1200)
                          #sizing_mode='stretch_width', width=900)
            cext([f"## {fname} <small>{file.path}</small>", ace, pn.layout.Divider()])

        return col

    #@depends_on_btn_click("structures_btn")
    #def on_structures_btn(self):
    #    what = ""
    #    if "input" in self.structures_io_checkbox.value: what += "i"
    #    if "output" in self.structures_io_checkbox.value: what += "o"
    #    dfs = self.flow.compare_structures(nids=self.nids,
    #                                       what=what,
    #                                       verbose=self.verbose, with_spglib=False, printout=False,
    #                                       with_colors=False)

    #    return pn.Row(dfc(dfs.lattice), sizing_mode="scale_width")

    def get_panel(self, as_dict=False, **kwargs):
        """Return tabs with widgets to interact with the flow."""
        d = {}

        # This stuff is computed lazyly when the tab is activated.
        #d["Input"] = pn.param.ParamMethod(self.get_inputs_view, lazy=True)
        d["Input"] = self.get_inputs_view()
        d["Output"] = self.get_main_text_outs_view()
        view = self.get_errs_view()
        if view is not None: d["ErrFiles"] = view

        super_d =  super().get_panel(as_dict=True)
        d.update(super_d)

        ##d["Structures"] = pn.Row(pn.Column(self.structures_io_checkbox, self.structures_btn), self

        if as_dict: return d

        return self.get_template_from_tabs(d, template=kwargs.get("template", None))
                                           #closable=False, dynamic=True)