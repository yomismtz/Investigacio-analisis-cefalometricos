from __future__ import annotations
from tkinter import filedialog,messagebox,simpledialog,ttk
_INSTALLED=False

def install(workspace_class):
    global _INSTALLED
    if _INSTALLED:return
    old=workspace_class._build_export
    def build(self):
        old(self);box=ttk.LabelFrame(self.export_tab,text=self.T('Respaldo Yornis','Yornis backup'),padding=8);box.pack(fill='x',pady=6);ttk.Button(box,text=self.T('Respaldo cifrado AES…','AES encrypted backup…'),command=lambda:self.yornis_encrypted_backup()).pack(side='left',padx=4)
    workspace_class._build_export=build
    def backup(self):
        if not self.study_id:return
        p=filedialog.asksaveasfilename(defaultextension='.zip',filetypes=[('Yornis backup ZIP','*.zip')])
        if not p:return
        secret=simpledialog.askstring('Yornis',self.T('Clave del respaldo. No se almacena en Yornis:','Backup passphrase. It is not stored by Yornis:'),show='•',parent=self)
        if not secret:return
        try:self.db.yornis_backup(self.study_id,p,secret);messagebox.showinfo('Yornis',self.T('Respaldo cifrado creado. Conserva la clave en un lugar seguro.','Encrypted backup created. Keep the passphrase in a safe place.'),parent=self)
        except Exception as exc:messagebox.showerror('Yornis',str(exc),parent=self)
    workspace_class.yornis_encrypted_backup=backup;_INSTALLED=True
