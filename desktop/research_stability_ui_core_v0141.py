from __future__ import annotations
from pathlib import Path
from tkinter import filedialog,messagebox
from research_protocol import minimum_landmarks

_INSTALLED=False

def install(workspace_class,scroll_checks_class):
    global _INSTALLED
    if _INSTALLED:return
    old_set_items=scroll_checks_class.set_items;old_set_all=scroll_checks_class.set_all
    def set_items(self,items,selected=None,command=None):self._bulk_change_command=command;return old_set_items(self,items,selected,command)
    def set_all(self,state):
        old_set_all(self,state);cb=getattr(self,'_bulk_change_command',None)
        if cb:cb()
    scroll_checks_class.set_items=set_items;scroll_checks_class.set_all=set_all
    old_save=workspace_class.save_protocol
    def save_protocol(self):
        if self.study_id:
            cfg=self.collect_protocol();self.db.update_study_info(self.study_id,cfg.get('title',''),cfg.get('researcher',''),cfg.get('institution',''),cfg.get('objective',''),bool(cfg.get('blind_mode')))
        return old_save(self)
    workspace_class.save_protocol=save_protocol
    def open_case(self,cid:int):
        if not self.study_id:return
        c=self.db.case(cid);pv=self.db.case_protocol_version(cid);p=self.db.protocol_by_version(self.study_id,pv);self.protocol=(p['config'] or {})|{'version':pv}
        if not self.protocol.get('selected_variables'):messagebox.showwarning('YomCeph',self.T('El protocolo de este caso no contiene resultados seleccionados.','This case protocol has no selected outcomes.'));return
        if not c['image_path'] or not Path(c['image_path']).exists():
            image=filedialog.askopenfilename(filetypes=[('Radiografías','*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.pdf')])
            if not image:return
            self.db.attach_image(cid,image);c=self.db.case(cid)
        try:self.image=self.load_pil(c['image_path']);self.image_path=c['image_path']
        except Exception as exc:messagebox.showerror('YomCeph',str(exc));return
        self._render_cache_key=None;self.case_id=cid;self.landmarks=minimum_landmarks(self.protocol['selected_variables']);self.points=self.load_autosave(cid) or self.db.latest_landmarks(cid,pv);self.landmark_index=0;self.undo_stack=[];self.redo_stack=[];self._drag_original=None
        s=self.db.study(self.study_id);self.mm_per_px=c['case_mm_per_px'] or s['study_mm_per_px'];self.db.mark_in_progress(cid);self.landmark_list.delete(0,'end')
        for name in self.landmarks:self.landmark_list.insert('end',name)
        if self.landmarks:self.landmark_list.selection_set(0)
        self.trace_case_title.config(text=f"#{c['case_number']} · {c['study_code']} · protocolo v{pv}")
        self.trace_meta.config(text=self.T('Modo ciego activo: edad/sexo ocultos','Blind mode active: age/sex hidden') if bool(s['blind_mode']) else f"{self.T('Sexo','Sex')}: {c['sex'] or '—'} · {self.T('Edad','Age')}: {c['age'] if c['age'] is not None else '—'}")
        self.calib_label.config(text=f"{self.mm_per_px:.6f} mm/px" if self.mm_per_px else self.T('Sin calibrar','Not calibrated'));self.tabs.select(self.trace_tab);self.fit_image();self.update_trace_progress();self.calculate_preview()
    workspace_class.open_case=open_case
    def canvas_click(self,e):
        if self.image is None:return
        p=self.canvas_to_image(e.x,e.y)
        if self.calibration_mode:
            self.calibration_clicks.append(p)
            if len(self.calibration_clicks)==2:
                import math
                d=math.dist(*self.calibration_clicks);self.mm_per_px=self.pending_mm/d if d>0 else None;self.calibration_mode=False;self.calibration_clicks=[];self.calib_label.config(text=f"{self.mm_per_px:.6f} mm/px" if self.mm_per_px else self.T('Sin calibrar','Not calibrated'));self.autosave()
            self.redraw();return
        near=self.nearest_point(e.x,e.y);k=near or self.current_landmark()
        if not k:return
        self._drag_original=(k,self.points.get(k));self.points[k]=p;self.dragging=k
        if near is None and self.landmark_index<len(self.landmarks)-1:self.step_landmark(1)
        self.update_trace_progress();self.redraw()
    def canvas_release(self,e):
        if not self.dragging:return
        k=self.dragging;final=self.points.get(k);original=getattr(self,'_drag_original',None)
        if original and original[0]==k and original[1]!=final:self.undo_stack.append((k,original[1],final));self.redo_stack.clear()
        self.autosave();self.dragging=None;self._drag_original=None;self.update_trace_progress()
    workspace_class.canvas_click=canvas_click;workspace_class.canvas_release=canvas_release
    _INSTALLED=True
