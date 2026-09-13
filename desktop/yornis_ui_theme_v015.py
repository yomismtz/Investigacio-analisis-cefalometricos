from __future__ import annotations
import tkinter as tk
from tkinter import simpledialog,ttk
import yornis_theme
from yomceph_theme import PALETTE,RESEARCH_STATUS,TRACING
_INSTALLED=False

def install(workspace_class):
    global _INSTALLED
    if _INSTALLED:return
    old_style=workspace_class._style
    def style(self):
        yornis_theme.apply_theme(yornis_theme.current_theme_name(),persist=False);old_style(self);apply_widget_style(self)
    workspace_class._style=style
    old_menu=workspace_class._build_menu
    def build_menu(self):
        old_menu(self);menu=self.nametowidget(self['menu']);appearance=tk.Menu(menu,tearoff=0)
        for name in yornis_theme.theme_names():appearance.add_command(label=name+(' · predeterminado' if name=='Agaporni' else ''),command=lambda n=name:change_theme(self,n))
        appearance.add_separator();appearance.add_command(label=self.T('Tamaño de puntos…','Landmark size…'),command=lambda:choose_radius(self));menu.add_cascade(label=self.T('APARIENCIA','APPEARANCE'),menu=appearance)
    workspace_class._build_menu=build_menu
    workspace_class.redraw=lambda self:redraw_small(self)
    _INSTALLED=True

def apply_widget_style(app):
    t=yornis_theme.THEMES[yornis_theme.current_theme_name()];app.configure(bg=t['bg']);s=ttk.Style(app)
    s.configure('TFrame',background=t['bg']);s.configure('Panel.TFrame',background=t['panel']);s.configure('Title.TLabel',background=t['bg'],foreground=t['primary_dark']);s.configure('Heading.TLabel',background=t['panel'],foreground=t['primary']);s.configure('Muted.TLabel',background=t['panel'],foreground=t['muted']);s.configure('Treeview',fieldbackground=t['panel'],background=t['panel'],foreground=t['text']);s.configure('Treeview.Heading',background=t['panel_alt'],foreground=t['primary_dark'])
    if hasattr(app,'canvas'):app.canvas.configure(bg=t['canvas'])
    if hasattr(app,'chart'):app.chart.configure(bg=t['panel'],highlightbackground=t['border'])
    if hasattr(app,'preview'):app.preview.configure(bg=t['canvas'])
    if hasattr(app,'magnifier'):app.magnifier.configure(bg=t['canvas'],highlightbackground=t['border'])
    if hasattr(app,'case_tree'):
        for key,st in RESEARCH_STATUS.items():app.case_tree.tag_configure(key,foreground=st['foreground'])

def change_theme(app,name):
    yornis_theme.apply_theme(name);apply_widget_style(app)
    if hasattr(app,'refresh_status_buttons'):app.refresh_status_buttons()
    if hasattr(app,'refresh_cases'):app.refresh_cases()
    if hasattr(app,'refresh_dashboard'):app.refresh_dashboard()
    if hasattr(app,'redraw'):app.redraw()
    app.status.config(text=app.T(f'Tema {name} aplicado',f'{name} theme applied'))

def choose_radius(app):
    value=simpledialog.askinteger('Yornis',app.T('Radio visible del punto (1–6 px). Recomendado: 2 px.','Visible landmark radius (1–6 px). Recommended: 2 px.'),initialvalue=yornis_theme.landmark_radius(),minvalue=1,maxvalue=6,parent=app)
    if value is not None:yornis_theme.set_landmark_radius(value);app.redraw()

def redraw_small(app):
    from PIL import Image,ImageTk
    r0=yornis_theme.landmark_radius();app.canvas.delete('all')
    if app.image is not None:
        w=max(1,int(app.image.width*app.zoom));h=max(1,int(app.image.height*app.zoom));key=(id(app.image),w,h)
        if getattr(app,'_render_cache_key',None)!=key:
            im=app.image.resize((w,h),Image.Resampling.LANCZOS);app.photo=ImageTk.PhotoImage(im);app._render_cache_key=key
        app.canvas.create_image(app.offx,app.offy,anchor='nw',image=app.photo)
    for k,p in app.points.items():
        if k not in app.landmarks:continue
        x,y=app.image_to_canvas(p);active=k==app.current_landmark();r=r0+1 if active else r0;fill=TRACING['landmark_active'] if active else TRACING['landmark']
        app.canvas.create_oval(x-r,y-r,x+r,y+r,fill=fill,outline=TRACING['selection_ring'],width=1)
        app.canvas.create_text(x+r+3,y-r-2,text=k,fill=TRACING['label'],anchor='sw',font=('Segoe UI',8,'bold'))
    if len(app.calibration_clicks)==1:
        x,y=app.image_to_canvas(app.calibration_clicks[0]);app.canvas.create_oval(x-3,y-3,x+3,y+3,fill=PALETTE['mint_300'])
