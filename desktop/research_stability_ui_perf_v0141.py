from __future__ import annotations
from pathlib import Path
from tkinter import filedialog,messagebox
from research_protocol import trace_qc

_INSTALLED=False

def install(workspace_class):
    global _INSTALLED
    if _INSTALLED:return
    def redraw(self):
        from PIL import Image,ImageTk
        from yomceph_theme import PALETTE,TRACING
        self.canvas.delete('all')
        if self.image is not None:
            w=max(1,int(self.image.width*self.zoom));h=max(1,int(self.image.height*self.zoom));key=(id(self.image),w,h)
            if getattr(self,'_render_cache_key',None)!=key:
                im=self.image.resize((w,h),Image.Resampling.LANCZOS);self.photo=ImageTk.PhotoImage(im);self._render_cache_key=key
            self.canvas.create_image(self.offx,self.offy,anchor='nw',image=self.photo)
        for k,p in self.points.items():
            if k not in self.landmarks:continue
            x,y=self.image_to_canvas(p);r=5 if k!=self.current_landmark() else 7;fill=TRACING['landmark_active'] if k==self.current_landmark() else TRACING['landmark'];self.canvas.create_oval(x-r,y-r,x+r,y+r,fill=fill,outline=TRACING['selection_ring'],width=2);self.canvas.create_text(x+8,y-8,text=k,fill=TRACING['label'],anchor='sw',font=('Segoe UI',9,'bold'))
        if len(self.calibration_clicks)==1:
            x,y=self.image_to_canvas(self.calibration_clicks[0]);self.canvas.create_oval(x-6,y-6,x+6,y+6,fill=PALETTE['mint_300'])
    workspace_class.redraw=redraw
    def import_metadata_csv(self):
        if not self.require_study():return
        path=filedialog.askopenfilename(filetypes=[('CSV','*.csv')])
        if not path:return
        meta=self.db.read_metadata_csv(path);updated=0;errors=[]
        for c in self.db.list_cases(self.study_id,include_excluded=True):
            md=meta.get(c['original_filename'],meta.get(Path(c['original_filename']).stem,meta.get(c['study_code'],{})))
            if not md:continue
            try:self.db.update_case_metadata(c['id'],sex=str(md.get('sex') or c['sex']),age=self.db._float_or_none(md.get('age')) if md.get('age') not in (None,'') else c['age'],study_code=str(md.get('id') or c['study_code']),examiner=str(md.get('examiner') or c['examiner']));updated+=1
            except Exception as exc:errors.append(f"{c['study_code']}: {exc}")
        self.refresh_cases();msg=self.T(f'Se actualizaron {updated} registros.',f'Updated {updated} records.')
        if errors:msg+='\n\n'+self.T('Errores:','Errors:')+'\n'+'\n'.join(errors[:12])
        messagebox.showinfo('YomCeph',msg)
    workspace_class.import_metadata_csv=import_metadata_csv
    def calculate_and_save(self):
        if not self.case_id:return
        results=self.calculate_preview();issues=trace_qc(self.protocol.get('selected_variables',[]),self.points,self.mm_per_px);soft=[x for x in issues if x.get('code')=='near_superimposed']
        if soft:
            if not messagebox.askyesno(self.T('Revisión QC','QC review'),self.T('Se detectaron landmarks casi superpuestos. ¿Guardar y marcar el caso para revisión?','Nearly superimposed landmarks were detected. Save and flag the case for review?'),parent=self):return
            self.db.set_review_flag(self.case_id,True)
        else:self.db.set_review_flag(self.case_id,False)
        self.db.save_trace(self.case_id,self.protocol['version'],self.points,results,[],self.mm_per_px);status=self.db.case(self.case_id)['status'];self.refresh_cases();self.refresh_dashboard();self.autosave()
        if status=='complete':messagebox.showinfo('YomCeph',self.T('Caso completo. Se marcó automáticamente en verde menta.','Case complete. It was automatically marked mint green.'))
        else:messagebox.showwarning('YomCeph',self.T('El caso se guardó pero aún no cumple todos los resultados del protocolo.','The case was saved but does not yet contain every protocol outcome.'))
    workspace_class.calculate_and_save=calculate_and_save
    _INSTALLED=True
