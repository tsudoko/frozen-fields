# Snowflake Icon
icon_name = "flake"
min_width = "28"

## Uncomment to use the Kubuntu icon instead of the snowflake icon
#icon_name = "frozen_26x28"
#min_width = "28"

from aqt import mw
from aqt import editor
from anki.hooks import wrap

from anki.utils import json

import os

def addons_folder(): return mw.pm.addonFolder()

def icon_color(icon, ext="png"):
    return "'" + os.path.join(addons_folder(),
                              "frozen_fields_addon",
                              "icons",
                              (icon + "_color." + ext)).replace("\\","/") + "'"

def icon_grayscale(icon, ext="png"):
    return "'" + os.path.join(addons_folder(),
                              "frozen_fields_addon",
                              "icons",
                              (icon + "_grayscale." + ext)).replace("\\","/") + "'"


js_code = """
function onFrozen(elem) {
    currentField = elem;
    py.run("frozen:" + currentField.id.substring(1));
}

function setFrozenFields(fields, frozen, focusTo) {
    var txt = "";
    for (var i=0; i<fields.length; i++) {
        var n = fields[i][0];
        var f = fields[i][1];
        if (!f) {
            f = "<br>";
        }
        txt += "<tr><td style='min-width:""" + min_width + """'></td><td class=fname>{0}</td></tr><tr>".format(n);
        if (frozen[i]) {
            txt += "<td style='min-width:""" + min_width + """'><div id=i{0} onclick='onFrozen(this);'><img src=""" + icon_color(icon_name) + """/></div></td>".format(i);
        }
        else {
            txt += "<td style='min-width:"""  + min_width + """'><div id=i{0} onclick='onFrozen(this);'><img src=""" + icon_grayscale(icon_name) + """/></div></td>".format(i);
        }
        txt += "<td width=100%%>"
        txt += "<div id=f{0} onkeydown='onKey();' onmouseup='onKey();'".format(i);
        txt += " onfocus='onFocus(this);' onblur='onBlur();' class=field ";
        txt += "ondragover='onDragOver(this);' ";
        txt += "contentEditable=true class=field>{0}</div>".format(f);
        txt += "</td>"
        txt += "</td></tr>";
    }
    $("#fields").html("<table cellpadding=0 width=100%%>"+txt+"</table>");
    if (!focusTo) {
        focusTo = 0;
    }
    if (focusTo >= 0) {
        $("#f"+focusTo).focus();
    }
};
"""


def myLoadNote(self):
    self.web.eval(js_code)
    if self.stealFocus:
        field = self.currentField
    else:
        field = -1
    if not self._loaded:
        # will be loaded when page is ready
        return
    data = []
    for fld, val in self.note.items():
        data.append((fld, self.mw.col.media.escapeImages(val)))
    ###########################################################
    sticky = []
    model = self.note.model()
    for fld in model['flds']:
        sticky.append(fld['sticky'])
    ###########################################################
    self.web.eval("setFrozenFields(%s, %s, %d);" % (
        json.dumps(data), json.dumps(sticky), field))
    self.web.eval("setFonts(%s);" % (
        json.dumps(self.fonts())))
    self.checkValid()
    self.widget.show()
    if self.stealFocus:
        self.web.setFocus()

def myBridge(self, str):
    if str.startswith("frozen"):
        (cmd, txt) = str.split(":", 1)
        field_nr = int(txt)
        model = self.note.model()
        is_sticky = model['flds'][field_nr]['sticky']
        model['flds'][field_nr]['sticky'] = not is_sticky
        self.loadNote()

editor.Editor.loadNote = myLoadNote
editor.Editor.bridge = wrap(editor.Editor.bridge, myBridge, 'before')