from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
import mysql

#Top level vinduer
#Top level for studentajourhold
def studenter():
    #defs
    #Knapp for å kunne velge flere studenter for bruk i slett
    def velg_fler():
        status=flervalg.get()
        if status == 1:
            lst_studenter['selectmode']=EXTENDED
        else:
            lst_studenter['selectmode']=SINGLE

    #Funksjon for å gjøre alle feltene tilgjengelige for endring for bruk i legg til og endre
    def open_ent():
        radios = (ent_fornavn, ent_etternavn, ent_epost, ent_tlf)
        for radio in range(4):
            radios[radio]['state'] = 'normal'

    #Funksjon for å tømme alle feltene. Brukes ved slett og legg til (for å tømme feltene)
    def empty():
        studentnr.set('')
        fornavn.set('')
        etternavn.set('')
        epost.set('')
        tlf.set('')

    # Funksjon for å gjøre et felt tilgjengelig for endring og de andre til readonly
    def rd_edit():
        radios=(ent_fornavn, ent_etternavn, ent_epost, ent_tlf)
        valgt=edit.get()
        for radio in range(4):
            if radio!=valgt:
                radios[radio]['state']='readonly'
            else:
                radios[radio]['state']='normal'

    #Funksjon for å slette valgte studenter med tilhørende eksamensresultater fra databasen
    def slett():
        def slett1():
            mengde = lst_studenter.curselection()
            slett_student_markor = mindatabase.cursor()
            for student in mengde:
                slett_karakterer = ("DELETE FROM Eksamensresultat "
                                    "WHERE Studentnr = %s")
                slett_student = ("DELETE FROM Student "
                                "WHERE Studentnr = %s")
                slett_student_markor.execute(
                    slett_karakterer, (lst_studenter.get(student),))
                slett_student_markor.execute(
                    slett_student, (lst_studenter.get(student),))
            mindatabase.commit()
            slett_student_markor.close()
            listeinnhold()
            edit.set(value=4)
            rd_edit()
            empty()
            lst_studenter.selection_clear(0, 'end')
            top_sikker.destroy()

        def sikker():
            resultater = []
            mengde = lst_studenter.curselection()
            student_markor = mindatabase.cursor()
            for student in mengde:
                sporring = ("SELECT COUNT(Studentnr) AS Eksamner "
                            "FROM eksamensresultat "
                            "WHERE Studentnr = %s "
                            "GROUP BY Studentnr" % lst_studenter.get(student))
                student_markor.execute(sporring)
                fetch = student_markor.fetchone()
                if fetch != None:
                    resultater += fetch
                else:
                    resultater += (0,)
            student_markor.close()

            if len(resultater) == 1:
                lbl_sikker['text'] = (
                    'Er du sikker på at du vil slette student: %s \nog %s tillhørende eksamensresultater?' % (lst_studenter.get(mengde[0]), resultater[0]))
            else:
                antall_karakterer = 0
                for kar in resultater:
                    antall_karakterer += kar
                lbl_sikker['text'] = (
                    'Er du sikker på at du vil slette %s studenter\nog %s eksamensresultater?' % (len(resultater), antall_karakterer))

        top_sikker = Toplevel(top_studenter)
        top_sikker.title('Er du sikker?')

        lbl_sikker = Label(top_sikker)
        lbl_sikker.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        btn_ja = Button(top_sikker, text='JA', command=slett1)
        btn_ja.grid(row=1, column=0, padx=10, pady=10)
        btn_nei = Button(top_sikker, text='Nei', command=top_sikker.destroy)
        btn_nei.grid(row=1, column=1, padx=10, pady=10)

        sikker()

    #Funksjon for å endre poster i studenttabellen
    def endre():
        kolonner=('Fornavn', 'Etternavn', 'Epost', 'Telefon')
        inndata = (fornavn.get(), etternavn.get(), epost.get(), tlf.get())
        student_markor=mindatabase.cursor()
        sporring = (
        "UPDATE Student "
        "SET %s='%s' "
        "WHERE Studentnr='%s'") % (kolonner[edit.get()], inndata[edit.get()], studentnr.get())
        #nye=(kolonner[edit.get()], inndata[edit.get()], studentnr.get())
        #nye = (inndata[edit.get()], studentnr.get())

        student_markor.execute(sporring)
        mindatabase.commit()
        student_markor.close()
        edit.set(value=4)
        rd_edit()
        
    #Funksjon for å legge til poster i studenttabellen
    def legg_til():
        student_markor=mindatabase.cursor()
        inndata=(studentnr.get(),fornavn.get(),etternavn.get(),epost.get(),tlf.get())
        sporring = ("INSERT INTO Student "
                    "(Studentnr, Fornavn, Etternavn, Epost, Telefon) "
                    "VALUES(%s,%s,%s,%s,%s)")
        student_markor.execute(sporring, inndata)
        mindatabase.commit()
        student_markor.close()
        listeinnhold()
        lst_studenter.select_clear(0, 'end')
        #lst_studenter.activate('end')
        lst_studenter.selection_set('end')
        lst_studenter.see('end')
        lst_studenter.event_generate("<<ListboxSelect>>")
        
    #Funksjon for å vise eksamensresultater for valgt student
    def eksamensres():
        stnr=studentnr.get()
        def lagre_karakter():
            rad = tvw_eksamensres.focus()
            karakter = ent_karakter.get()
            dato = tvw_eksamensres.item(rad)['values'][4]
            db_cursor = mindatabase.cursor()
            query = ("UPDATE Eksamensresultat "
                    "SET Karakter = %s "
                    "WHERE Studentnr = %s "
                    "AND Dato = %s")
            var = (karakter, stnr, dato)
            db_cursor.execute(query, var)
            mindatabase.commit()
            db_cursor.close()
            tvw_eksamensres.delete(*tvw_eksamensres.get_children())
            eksdata()

        def eks_slett():
            rad = tvw_eksamensres.focus()

            if rad != '':
                dato = tvw_eksamensres.item(rad)['values'][4]
                ekskar_cursor = mindatabase.cursor()
                query = ("DELETE FROM Eksamensresultat "
                        "WHERE Studentnr = %s "
                        "AND Dato = %s")
                var = (stnr, dato)
                ekskar_cursor.execute(query, var)
                mindatabase.commit()
                ekskar_cursor.close()
                tvw_eksamensres.delete(*tvw_eksamensres.get_children())
                eksdata()

        def eksdata():
            db_cursor = mindatabase.cursor()
            query = ("SELECT Eksamensresultat.Emnekode, Emnenavn, Studiepoeng, Karakter, Dato "
                    "FROM Eksamensresultat RIGHT JOIN Emne "
                    "ON Eksamensresultat.Emnekode = Emne.Emnekode "
                    "WHERE Studentnr = %s "
                    "ORDER BY Eksamensresultat.Dato DESC")
            db_cursor.execute(query, (stnr,))
            row = db_cursor.fetchone()
            count = 0
            stp = 0
            while row != None:
                stp += row[2]
                tvw_eksamensres.insert('', index=count, text='', values=(
                    row[0], row[1], row[2], row[3], row[4]))
                row = db_cursor.fetchone()
                count += 1
            db_cursor.close()
            studiepoeng.set(stp)

        def getkar(event):
            rad = tvw_eksamensres.focus()
            if rad != '':
                kar = tvw_eksamensres.item(rad)['values'][3]
                karakter.set(kar)

        top_eksamensres = Toplevel(window)
        top_eksamensres.title("Eksamensresultater")

        lbl_eksamensres = Label(top_eksamensres, text="Eksamensresultater:")
        lbl_eksamensres.grid(row=0, column=0, padx=10, pady=(5, 0), sticky=NW)
        lbl_studiepoeng = Label(top_eksamensres, text="Studiepoeng:")
        lbl_studiepoeng.grid(row=1, column=2, padx=10, pady=(5, 0), sticky=NW)
        lbl_karakter = Label(top_eksamensres, text="Karakter:")
        lbl_karakter.grid(row=4, column=2, padx=10, pady=(5, 0), sticky=SW)

        studiepoeng = StringVar()
        ent_studiepoeng = Entry(top_eksamensres, width=10,
                                state='readonly', textvariable=studiepoeng)
        ent_studiepoeng.grid(row=2, column=2, padx=10, pady=(0, 5), sticky=NW)
        karakter = StringVar()
        ent_karakter = Entry(top_eksamensres, width=10, textvariable=karakter)
        ent_karakter.grid(row=5, column=2, padx=10, pady=(0, 5), sticky=NW)

        btn_endre_karakter = Button(top_eksamensres, text="Endre", command=lagre_karakter)
        btn_endre_karakter.grid(row=6, column=2, padx=10, sticky=NW)
        btn_slett_eks = Button(top_eksamensres, text="Slett", command=eks_slett)
        btn_slett_eks.grid(row=10, column=2, padx=10, pady=5, sticky=W)

        btn_eksdata_lukk = Button(top_eksamensres, text="Lukk", command=top_eksamensres.destroy)
        btn_eksdata_lukk.grid(row=15, column=2, padx=5, pady=5, sticky=SE)


        scroll_tvw = ttk.Scrollbar(top_eksamensres, orient="vertical")
        scroll_tvw.grid(row=1, column=1, rowspan=15, sticky=NS)

        tvw_eksamensres = ttk.Treeview(top_eksamensres, columns=("Emnekode", "Emnenavn", "Studiepoeng", "Karakter", "Dato"), yscrollcommand=scroll_tvw.set)
        tvw_eksamensres.column("#0", width=0, stretch=NO)
        tvw_eksamensres.column("Emnekode", width=70)
        tvw_eksamensres.column("Emnenavn", width=200)
        tvw_eksamensres.column("Studiepoeng", width=90)
        tvw_eksamensres.column("Karakter", width=60)
        tvw_eksamensres.column("Dato", width=80)

        tvw_eksamensres.heading("#0", text="")
        tvw_eksamensres.heading("Emnekode", text="Emnekode", anchor=W)
        tvw_eksamensres.heading("Emnenavn", text="Emnenavn", anchor=W)
        tvw_eksamensres.heading("Studiepoeng", text="Studiepoeng", anchor=W)
        tvw_eksamensres.heading("Karakter", text="Karakter", anchor=W)
        tvw_eksamensres.heading("Dato", text="Dato", anchor=W)
        tvw_eksamensres.grid(row=1, column=0, rowspan=15, padx=(10, 0), pady=10, sticky=E)

        tvw_eksamensres.bind("<<TreeviewSelect>>", getkar)

        scroll_tvw['command'] = tvw_eksamensres.yview

        eksdata()
    
    #Funksjon for å vise vitnemål for valgt student
    def vitnemal():

        top_vitnemal = Toplevel()
        top_vitnemal.title("Vitnemål")


        scroll_vitnemal = ttk.Scrollbar(top_vitnemal, orient=VERTICAL)
        scroll_vitnemal.grid(row=1, column=1, padx=(0, 10), pady=10, rowspan=15, sticky=NS)
        # definerer tabell
        tvw_vitnemal = ttk.Treeview(top_vitnemal, columns=(
            'Emnekode', 'Emnenavn', 'Studiepoeng', 'Karakter', 'Dato'), yscrollcommand=scroll_vitnemal.set)
        tvw_vitnemal.column('#0', width=0, stretch=NO)
        tvw_vitnemal.column('Emnekode', width=100)
        tvw_vitnemal.column('Emnenavn', width=100)
        tvw_vitnemal.column('Studiepoeng', width=100)
        tvw_vitnemal.column('Karakter', width=100)
        tvw_vitnemal.column('Dato', width=100)

        tvw_vitnemal.heading('#0', text='')
        tvw_vitnemal.heading('Emnekode', text='Emnekode')
        tvw_vitnemal.heading('Emnenavn', text='Emnenavn')
        tvw_vitnemal.heading('Studiepoeng', text='Studiepoeng')
        tvw_vitnemal.heading('Karakter', text='Karakter')
        tvw_vitnemal.heading('Dato', text='Dato')
        tvw_vitnemal.grid(row=1, column=0, padx=(10, 0), pady=10, rowspan=15)

        scroll_vitnemal['command'] = tvw_vitnemal.yview

        # definerer widgets
        lbl_vitnemal = Label(top_vitnemal, text="Vitnemål:")
        lbl_vitnemal.grid(row=0, column=0, padx=10, pady=(10, 0), sticky=W)
        lbl_studiepoeng = Label(top_vitnemal, text="Sum Studiepoeng:")
        lbl_studiepoeng.grid(row=1, column=2, padx=10, pady=(10, 0), sticky=W)

        studiepoeng = StringVar()
        ent_studiepoeng = Entry(
            top_vitnemal, textvariable=studiepoeng, state='readonly')
        ent_studiepoeng.grid(row=2, column=2, padx=10, pady=(0, 10))

        btn_vitnemal_lukk = Button(top_vitnemal, text="Lukk", command=top_vitnemal.destroy)
        btn_vitnemal_lukk.grid(row=15, column=2, padx=5, pady=5, sticky=SE)

        # henter data fra databasen
        stnr = studentnr.get()
        vitnemal_cursor = mindatabase.cursor()
        query = ("SELECT NoKar.Emnekode, NoKar.Emnenavn, NoKar.Studiepoeng, Karakter, Nokar.Dato "
                "FROM(SELECT StudentNr, Eksamensresultat.Emnekode, Emnenavn, Studiepoeng, MAX(Dato) AS Dato "
                "FROM Eksamensresultat, Emne "
                "WHERE Eksamensresultat.Emnekode=Emne.Emnekode "
                "GROUP BY Studentnr, Emnekode, Emnenavn, Studiepoeng "
                "HAVING Studentnr=%s) AS NoKar, Eksamensresultat "
                "WHERE NoKar.Dato=Eksamensresultat.Dato AND NoKar.StudentNr=Eksamensresultat.StudentNr "
                "ORDER BY RIGHT(NoKar.Emnekode, 4);")
        vitnemal_cursor.execute(query, (stnr,))
        row = vitnemal_cursor.fetchone()
        count = 0
        stp = 0
        while row != None:
            stp += row[2]
            tvw_vitnemal.insert('', index=count, text='', values=(
                row[0], row[1], row[2], row[3], row[4]))
            row = vitnemal_cursor.fetchone()
            count += 1
        vitnemal_cursor.close()
        studiepoeng.set(stp)

    #Funksjon for å hente ut valgt student fra listen og vise i tekstboksene
    def hent_studenter(event):
        if len(lst_studenter.curselection()) == 1:
            valgt = lst_studenter.get(lst_studenter.curselection())
            student_markor = mindatabase.cursor()
            student_markor.execute('SELECT Studentnr, Fornavn, Etternavn, Epost, Telefon FROM Student')

            legg_til_modus = True
            for row in student_markor:
                if valgt == row[0]:
                    studentnr.set(row[0])
                    fornavn.set(row[1])
                    etternavn.set(row[2])
                    epost.set(row[3])
                    tlf.set(row[4])
                    legg_til_modus=False
            student_markor.close()

            if legg_til_modus:
                #kode for å åpne legg til modus
                empty()
                open_ent()

                lbl_velg.grid_remove()
                rd_velg.grid_remove()
                rd_fornavn.grid_remove()
                rd_etternavn.grid_remove()
                rd_epost.grid_remove()
                rd_tlf.grid_remove()

                btn_slett.grid_remove()
                chk_slett.grid_remove()
                btn_endre.grid_remove()
                btn_eksamensres.grid_remove()
                btn_vitnemal.grid_remove()
                btn_ny.grid(row=4, column=5, padx=15, pady=5, sticky=W)

                #Finner Neste tall for student
                nr_markor=mindatabase.cursor()
                nr_markor.execute("SELECT MAX(ABS(Studentnr)) "
                                "FROM Student;")
                nytt_tall=str(int(nr_markor.fetchone()[0])+1)
                studentnr.set(str(nytt_tall))
                nr_markor.close()
            else:
                lbl_velg.grid(row=2, column=3, padx=(0, 15), pady=5, sticky=E)
                
                rd_velg.grid(row=2, column=2, padx=(15, 0), pady=5, sticky=W)
                rd_fornavn.grid(row=3, column=2, padx=(15, 0), pady=5, sticky=W)
                rd_etternavn.grid(row=4, column=2, padx=(15, 0), pady=5, sticky=W)
                rd_epost.grid(row=5, column=2, padx=(15, 0), pady=5, sticky=W)
                rd_tlf.grid(row=6, column=2, padx=(15, 0), pady=5, sticky=W)

                btn_endre.grid(row=2, column=5, padx=15, pady=5, sticky=W)
                btn_slett.grid(row=3, column=5, padx=15, pady=5, sticky=W)
                chk_slett.grid(row=4, column=5, padx=10, sticky=NE)
                btn_eksamensres.grid(row=5, column=5, padx=15, pady=5, sticky=W)
                btn_vitnemal.grid(row=6, column=5, padx=15, pady=5, sticky=W)
                btn_ny.grid_remove()

                edit.set(value=4)
                rd_edit()


    # Funksjon for å hente ut alle studenter fra databasen og vise i listen
    def listeinnhold():
        student_markor = mindatabase.cursor()
        student_markor.execute("SELECT Studentnr FROM Student ORDER BY ABS(Studentnr)")
        studenter=['(Registrer Ny)']
        for row in student_markor:
            studenter+=row
        student_markor.close()
        innhold_i_lst_studenter.set(tuple(studenter))


    legg_til_modus=False
    top_studenter = Toplevel(window)
    top_studenter.title('Studenter')

    scroll = Scrollbar(top_studenter, orient=VERTICAL)
    scroll.grid(row=1, column=1, rowspan=10, padx=(0, 10), pady=5, sticky=NS)

    innhold_i_lst_studenter=StringVar()
    lst_studenter = Listbox(top_studenter, listvariable=innhold_i_lst_studenter, yscrollcommand=scroll.set, width=15, selectmode=SINGLE)
    lst_studenter.grid(row=1, column=0, rowspan=10, padx=(10, 0), pady=5, sticky=NS)

    listeinnhold()


    scroll['command']=lst_studenter.yview

    lbl_studenter = Label(top_studenter, text='Studenter:')
    lbl_studenter.grid(row=0, column=0, padx=(0, 15), pady=5, sticky=W)
    lbl_studentnr=Label(top_studenter, text='Studentnr:')
    lbl_studentnr.grid(row=0, column=3, padx=(0, 15), pady=5, sticky=E)
    lbl_velg = Label(top_studenter, text='Velg for å ende')
    lbl_velg.grid(row=2, column=3, padx=(0, 15), pady=5, sticky=E)
    lbl_fornavn = Label(top_studenter, text='Fornavn:')
    lbl_fornavn.grid(row=3, column=3, padx=(0, 15), pady=5, sticky=E)
    lbl_etternavn = Label(top_studenter, text='Etternavn:')
    lbl_etternavn.grid(row=4, column=3, padx=(0, 15), pady=5, sticky=E)
    lbl_epost = Label(top_studenter, text='E-Post:')
    lbl_epost.grid(row=5, column=3, padx=(0, 15), pady=5, sticky=E)
    lbl_tlf = Label(top_studenter, text='Tlf:')
    lbl_tlf.grid(row=6, column=3, padx=(0, 15), pady=5, sticky=E)

    studentnr = StringVar()
    ent_studentnr=Entry(top_studenter, width=6, textvariable=studentnr, state='readonly')
    ent_studentnr.grid(row=0, column=4, padx=(0, 15), pady=5, sticky=W)
    fornavn = StringVar()
    ent_fornavn = Entry(top_studenter, width=13, textvariable=fornavn, state='readonly')
    ent_fornavn.grid(row=3, column=4, padx=(0, 15), pady=5, sticky=W)
    etternavn = StringVar()
    ent_etternavn = Entry(top_studenter, width=14, textvariable=etternavn, state='readonly')
    ent_etternavn.grid(row=4, column=4, padx=(0, 15), pady=5, sticky=W)
    epost = StringVar()
    ent_epost = Entry(top_studenter, width=35, textvariable=epost, state='readonly')
    ent_epost.grid(row=5, column=4, padx=(0, 15), pady=5, sticky=W)
    tlf = StringVar()
    ent_tlf = Entry(top_studenter, width=10, textvariable=tlf, state='readonly')
    ent_tlf.grid(row=6, column=4, padx=(0, 15), pady=5, sticky=W)

    edit = IntVar(value=4)
    rd_velg = Radiobutton(top_studenter, variable=edit, value=4, command=rd_edit)
    rd_velg.grid(row=2, column=2, padx=(15, 0), pady=5, sticky=W)
    rd_fornavn = Radiobutton(top_studenter, variable=edit, value=0, command=rd_edit)
    rd_fornavn.grid(row=3, column=2, padx=(15, 0), pady=5, sticky=W)
    rd_etternavn = Radiobutton(top_studenter, variable=edit, value=1, command=rd_edit)
    rd_etternavn.grid(row=4, column=2, padx=(15, 0), pady=5, sticky=W)
    rd_epost = Radiobutton(top_studenter, variable=edit, value=2, command=rd_edit)
    rd_epost.grid(row=5, column=2, padx=(15, 0), pady=5, sticky=W)
    rd_tlf = Radiobutton(top_studenter, variable=edit, value=3, command=rd_edit)
    rd_tlf.grid(row=6, column=2, padx=(15, 0), pady=5, sticky=W)


    btn_endre=Button(top_studenter, text='Endre', command=endre)
    btn_endre.grid(row=2, column=5, padx=15, pady=5, sticky=W)
    btn_slett=Button(top_studenter, text='Slett', command=slett)
    btn_slett.grid(row=3, column=5, padx=15, pady=5, sticky=W)
    btn_ny = Button(top_studenter, text='Ny student', command=legg_til)
    btn_ny.grid_remove()
    btn_eksamensres = Button(top_studenter, text='Eksamensresultater', command=eksamensres)
    btn_eksamensres.grid(row=5, column=5, padx=15, pady=5, sticky=W)
    btn_vitnemal = Button(top_studenter, text='Vitnemål', command=vitnemal)
    btn_vitnemal.grid(row=6, column=5, padx=15, pady=5, sticky=W)
    btn_lukk = Button(top_studenter, text='Lukk', command=top_studenter.destroy)
    btn_lukk.grid(row=7, column=5, padx=5, pady=5, sticky=SE)

    flervalg=IntVar()
    chk_slett = Checkbutton(top_studenter, text='Slett flere studenter samtidig', variable=flervalg, onvalue=1, offvalue=0, command=velg_fler)
    chk_slett.grid(row=4,column=5,padx=10, sticky=NE)

    lst_studenter.bind('<<ListboxSelect>>', hent_studenter)

def eksamner():
    def kar_reg():
        def lagre():
            # Legger alle studenter med og uten karakter i en 2-dimensjonal tuple
            list_stud = []
            for rad in tvw_medKarakter.get_children():
                list_stud += (tvw_medKarakter.item(rad)['values'][0], tvw_medKarakter.item(rad)['values'][3]),
            for rad in lst_utenKarakter.get(0, END):
                list_stud += (rad, None),
            # Oppdaterer databasen med de nye karakterene
            ekskar_cursor = mindatabase.cursor()
            query = ("UPDATE Eksamensresultat "
                    "SET Karakter = %s "
                    "WHERE Studentnr = %s "
                    "AND Dato = %s")

            for rad in list_stud:
                list_var = (rad[1], rad[0], dato)
                ekskar_cursor.execute(query, list_var)
            mindatabase.commit()
            ekskar_cursor.close()
            messagebox.showinfo('Karakterer registrert',
                                'Karakterene er nå registrert i databasen.')
            top_kar.destroy()

        def red_med(event):
            rad = tvw_medKarakter.focus()
            if rad != '':
                lst_utenKarakter.selection_clear(0, END)
                studnr.set(tvw_medKarakter.item(rad)['values'][0])
                karakter.set(tvw_medKarakter.item(rad)['values'][3])
            else:
                rad = lst_utenKarakter.curselection()
                if rad != '':
                    studnr.set(lst_utenKarakter.get(rad))
                    karakter.set('')

        def red_uten(event):
            tvw_medKarakter.focus('')
            tvw_medKarakter.selection_remove(tvw_medKarakter.selection())

        def flytt():
            innhold_stud = studnr.get()
            navn_cursor = mindatabase.cursor()
            query = ("SELECT Fornavn, Etternavn "
                    "FROM Student "
                    "WHERE Studentnr = %s")
            navn_cursor.execute(query, (innhold_stud,))
            navn = navn_cursor.fetchone()
            navn_cursor.close()
            innhold_kar = karakter.get()
            if innhold_kar == 'A' or innhold_kar == 'B' or innhold_kar == 'C' or innhold_kar == 'D' or innhold_kar == 'E' or innhold_kar == 'F' and innhold_stud != '':
                tvw_medKarakter.insert(
                    '', 0, values=(innhold_stud, navn[0], navn[1], innhold_kar))
                lst_utenKarakter.delete(lst_utenKarakter.curselection())
                studnr.set('')
                karakter.set('')
                lst_utenKarakter.selection_set(0)
                lst_utenKarakter.event_generate('<<ListboxSelect>>')
            else:
                if innhold_stud == '':
                    melding = 'Du må velge en student for å legge til karakteren i "Registrert" tabellen.'
                else:
                    if innhold_kar != '':
                        melding = 'Du må skrive inn en karakter mellom A-F (Store Bokstaver) for å legge til studenten i "Med karakter" tabellen.'
                    else:
                        melding = 'Du må skrive inn en karakter for å legge til studenten i "Registrert" tabellen.'
                messagebox.showerror(title='Feil!', message=melding)

        def flytt_tilbake():
            rad = tvw_medKarakter.focus()
            if rad != '':
                lst_utenKarakter.insert(
                    0, tvw_medKarakter.item(rad)['values'][0])
                tvw_medKarakter.delete(rad)
                studnr.set('')
                karakter.set('')
                lst_utenKarakter.selection_set(0)
                lst_utenKarakter.event_generate('<<ListboxSelect>>')
            else:
                messagebox.showerror(
                    title='Feil!', message='Du må velge en student i "Registrert" tabellen for å flytte tilbake til "Ikke Registrert" tabellen.')

        top_kar = Toplevel(top_eksamen)
        top_kar.title('Karakterer - %s - %s' % (tvw_eksamen.item(tvw_eksamen.selection())['values'][0], tvw_eksamen.item(tvw_eksamen.selection())['values'][2]))

        scroll_utenKarakter = Scrollbar(top_kar, orient=VERTICAL)
        scroll_utenKarakter.grid(row=1, column=1, padx=(0, 10), pady=10, rowspan=10, sticky=NS)
        scroll_medKarakter = Scrollbar(top_kar, orient=VERTICAL)
        scroll_medKarakter.grid(row=1, column=5, padx=(0, 10), pady=10, rowspan=10, sticky=NS)

        # definerer tabell
        innhold_lst_utenKarakter = StringVar()
        lst_utenKarakter = Listbox(top_kar, width=10, height=13, yscrollcommand=scroll_utenKarakter.set,
                                    listvariable=innhold_lst_utenKarakter, exportselection=False)
        lst_utenKarakter.grid(row=1, column=0, padx=(10, 0), pady=10, rowspan=10, sticky=NSEW)
        scroll_utenKarakter['command'] = lst_utenKarakter.yview

        tvw_medKarakter = ttk.Treeview(top_kar, columns=(
            'StudentNr', 'Fornavn', 'Etternavn', 'Karakter'), show='headings', yscrollcommand=scroll_medKarakter.set)
        tvw_medKarakter.column('#0', stretch=NO)
        tvw_medKarakter.column('StudentNr', width=70)
        tvw_medKarakter.column('Fornavn', width=60)
        tvw_medKarakter.column('Etternavn', width=60)
        tvw_medKarakter.column('Karakter', width=60)

        tvw_medKarakter.heading('#0', text='')
        tvw_medKarakter.heading('StudentNr', text='StudentNr')
        tvw_medKarakter.heading('Fornavn', text='Fornavn')
        tvw_medKarakter.heading('Etternavn', text='Etternavn')
        tvw_medKarakter.heading('Karakter', text='Karakter')
        tvw_medKarakter.grid(row=1, column=4, padx=(10, 0), pady=10, rowspan=10, sticky=NSEW)
        scroll_medKarakter['command'] = tvw_medKarakter.yview

        # definerer widgets
        lbl_utenKarakter = Label(top_kar, text='Ikke Registrert:')
        lbl_utenKarakter.grid(row=0, column=0, padx=10, pady=5, sticky=W)
        lbl_medKarakter = Label(top_kar, text='Registrert:')
        lbl_medKarakter.grid(row=0, column=4, padx=10, pady=5, sticky=W)
        lbl_studnr = Label(top_kar, text='Studnr:')
        lbl_studnr.grid(row=1, column=2, padx=10, pady=5, sticky=W)
        lbl_karakter = Label(top_kar, text='Karakter:')
        lbl_karakter.grid(row=2, column=2, padx=10, pady=5, sticky=W)

        studnr = StringVar()
        ent_studnr = Entry(top_kar, textvariable=studnr, state='readonly')
        ent_studnr.grid(row=1, column=3, padx=10, pady=5, sticky=W)
        karakter = StringVar()
        ent_karakter = Entry(top_kar, textvariable=karakter)
        ent_karakter.grid(row=2, column=3, padx=10, pady=5, sticky=W)

        btn_legg_til = Button(top_kar, text='>>>', command=flytt)
        btn_legg_til.grid(row=3, column=3, padx=10, pady=(5, 1), sticky=SW)
        btn_fjern = Button(top_kar, text='<<<', command=flytt_tilbake)
        btn_fjern.grid(row=4, column=3, padx=10, pady=(1, 5), sticky=NW)
        btn_lagre = Button(top_kar, text='Lagre Karakterer', command=lagre)
        btn_lagre.grid(row=10, column=2, columnspan=2, padx=10, pady=5)
        btn_karReg_lukk = Button(top_kar, text='Lukk', command=top_kar.destroy)
        btn_karReg_lukk.grid(row=11, column=5, padx=5, pady=5, sticky=SE)

        lst_utenKarakter.bind('<<ListboxSelect>>', red_uten)
        tvw_medKarakter.bind('<<TreeviewSelect>>', red_med)

        # Henter ut studenter uten karakter for eksamen
        dato = tvw_eksamen.item(tvw_eksamen.selection())['values'][2]
        emnekode = tvw_eksamen.item(tvw_eksamen.selection())['values'][0]
        studenter_cursor = mindatabase.cursor()
        query = ("SELECT Studentnr "
                "FROM Eksamensresultat "
                "WHERE Emnekode = %s "
                "AND Karakter IS NULL "
                "AND Dato = %s "
                "ORDER BY ABS(Studentnr) ASC")
        studenter_cursor.execute(query, (emnekode, dato))
        row = studenter_cursor.fetchone()
        count = 0
        studsUten = []
        while row != None:
            studsUten += [row[0]]
            row = studenter_cursor.fetchone()
            count += 1
        studenter_cursor.close()

        # Henter ut studenter med karakter for eksamen
        studenter_cursor = mindatabase.cursor()
        query = ("SELECT Eksamensresultat.Studentnr, Fornavn, Etternavn, Karakter "
                "FROM Eksamensresultat, Student "
                "WHERE Emnekode = %s "
                "AND Karakter IS NOT NULL "
                "AND Dato = %s "
                "AND Eksamensresultat.Studentnr = Student.Studentnr "
                "ORDER BY ABS(Eksamensresultat.Studentnr) ASC")
        studenter_cursor.execute(query, (emnekode, dato))
        row = studenter_cursor.fetchone()
        count = 0
        studsMed = []
        while row != None:
            studsMed += [row]
            row = studenter_cursor.fetchone()
            count += 1
        studenter_cursor.close()

        # Fyller listbox med studenter uten karakter
        for i in range(0, len(studsUten)):
            lst_utenKarakter.insert('end', studsUten[i])

        # Fyller treeview med studenter med karakter
        for i in range(0, len(studsMed)):
            tvw_medKarakter.insert(
                '', 'end', values=(studsMed[i][0], studsMed[i][1], studsMed[i][2], studsMed[i][3]))

    def karstat():
        top_stats = Toplevel()
        top_stats.title('Karakterstatistikk')

        # definerer widgets
        cvs_karstat = Canvas(top_stats, width=360, height=200)
        cvs_karstat.grid(row=0, column=0, padx=10, pady=10, rowspan=10)

        lbl_emnekode = Label(top_stats, text='Emnekode:')
        lbl_emnekode.grid(row=0, column=1, padx=10, pady=(5, 0), sticky=SE)
        lbl_emnenavn = Label(top_stats, text='Emnenavn:')
        lbl_emnenavn.grid(row=1, column=1, padx=10, pady=0, sticky=E)
        lbl_studiepoeng = Label(top_stats, text='Studiepoeng:')
        lbl_studiepoeng.grid(row=2, column=1, padx=10, pady=(0, 5), sticky=NE)
        lbl_dato = Label(top_stats, text='Dato:')
        lbl_dato.grid(row=3, column=1, padx=10, pady=(5, 0), sticky=NE)
        lbl_antall = Label(top_stats, text='Antall:')
        lbl_antall.grid(row=4, column=1, padx=10, pady=(5, 0), sticky=SE)

        emnekode = StringVar()
        ent_emnekode = Entry(
            top_stats, textvariable=emnekode, state='readonly')
        ent_emnekode.grid(row=0, column=2, padx=10, pady=(5, 0), sticky=SW)
        emnenavn = StringVar()
        ent_emnenavn = Entry(
            top_stats, textvariable=emnenavn, state='readonly')
        ent_emnenavn.grid(row=1, column=2, padx=10, pady=0, sticky=E)
        studiepoeng = StringVar()
        ent_studiepoeng = Entry(
            top_stats, textvariable=studiepoeng, state='readonly')
        ent_studiepoeng.grid(row=2, column=2, padx=10, pady=(0, 5), sticky=NW)
        dato = StringVar()
        ent_dato = Entry(top_stats, textvariable=dato, state='readonly')
        ent_dato.grid(row=3, column=2, padx=10, pady=(5, 0), sticky=NW)
        antall = StringVar()
        ent_antall = Entry(top_stats, textvariable=antall, state='readonly')
        ent_antall.grid(row=4, column=2, padx=10, pady=(5, 0), sticky=SW)

        btn_lukk = Button(top_stats, text='Lukk', command=top_stats.destroy)
        btn_lukk.grid(row=9, column=2, padx=5, pady=5, sticky=SE)

        # Henter emneinfo
        emne_cursor = mindatabase.cursor()
        query = ("SELECT Emnekode, Emnenavn, Studiepoeng "
                "FROM Emne "
                "WHERE Emnekode = %s")
        emne_cursor.execute(query, (tvw_eksamen.item(
            tvw_eksamen.selection())['values'][0],))
        row = emne_cursor.fetchone()
        emne_cursor.close()

        # Fyller ut emneinfo
        emnekode.set(row[0])
        emnenavn.set(row[1])
        studiepoeng.set(row[2])
        dato.set(tvw_eksamen.item(tvw_eksamen.selection())['values'][2])

        # Henter ut karakterer for eksamen
        stat_emnekode = tvw_eksamen.item(tvw_eksamen.selection())['values'][0]
        stat_dato = tvw_eksamen.item(tvw_eksamen.selection())['values'][2]
        stat_cursor = mindatabase.cursor()
        query = ("SELECT Karakter "
                "FROM Eksamensresultat "
                "WHERE Emnekode = %s "
                "AND Dato = %s "
                "AND Karakter IS NOT NULL "
                "ORDER BY ABS(Studentnr) DESC")
        stat_cursor.execute(query, (stat_emnekode, stat_dato))
        row = stat_cursor.fetchone()
        count = 0
        stat_karakterer = []
        while row != None:
            stat_karakterer += [row[0]]
            row = stat_cursor.fetchone()
            count += 1
        stat_cursor.close()

        # Finner antall karakterer
        stat_kar = [0, 0, 0, 0, 0, 0]
        null = 0
        for i in range(0, len(stat_karakterer)):
            if stat_karakterer[i] == 'A':
                stat_kar[0] += 1
            else:
                if stat_karakterer[i] == 'B':
                    stat_kar[1] += 1
                else:
                    if stat_karakterer[i] == 'C':
                        stat_kar[2] += 1
                    else:
                        if stat_karakterer[i] == 'D':
                            stat_kar[3] += 1
                        else:
                            if stat_karakterer[i] == 'E':
                                stat_kar[4] += 1
                            else:
                                stat_kar[5] += 1

        # antall karakterer
        antall_kar = 0
        for i in range(0, len(stat_kar)):
            antall_kar += stat_kar[i]
        antall.set(antall_kar)

        # Finner prosentandel av karakterer
        stat_prosent = [0, 0, 0, 0, 0, 0]
        for i in range(0, len(stat_kar)):
            stat_prosent[i] = int((stat_kar[i]/len(stat_karakterer))*1000)
            stat_prosent[i] = stat_prosent[i]/10

        # Finner største prosentandel
        max_pro = 0
        for i in range(0, len(stat_prosent)):
            if stat_prosent[i] > max_pro:
                max_pro = stat_prosent[i]

        max_pro = max_pro+10

        convert = 150/max_pro
        hoyde = convert

        # Lager barchart
        cvs_karstat.create_line(50, 10, 50, 160, width=2)
        cvs_karstat.create_text(35, 10, text=str(max_pro)+'%', anchor=E)
        cvs_karstat.create_line(35, 10, 50, 10, width=1)
        cvs_karstat.create_text(35, 85, text=str(max_pro//2)+'%', anchor=E)
        cvs_karstat.create_line(35, 85, 50, 85, width=1)
        cvs_karstat.create_text(35, 159, text='0%', anchor=E)
        cvs_karstat.create_line(35, 159, 50, 159, width=1)

        cvs_karstat.create_rectangle(
            60, 160-stat_prosent[0]*hoyde, 90, 160, fill='green', outline='green')
        cvs_karstat.create_text(
            75, 180-stat_prosent[0]*hoyde-40, text=str(stat_prosent[0])+'%', anchor=N)
        cvs_karstat.create_text(75, 180, text='A - ' +
                                str(stat_kar[0]), anchor=S)

        cvs_karstat.create_rectangle(
            110, 160-stat_prosent[1]*hoyde, 140, 160, fill='green', outline='green')
        cvs_karstat.create_text(
            125, 180-stat_prosent[1]*hoyde-40, text=str(stat_prosent[1])+'%', anchor=N)
        cvs_karstat.create_text(125, 180, text='B - ' +
                                str(stat_kar[1]), anchor=S)

        cvs_karstat.create_rectangle(
            160, 160-stat_prosent[2]*hoyde, 190, 160, fill='green', outline='green')
        cvs_karstat.create_text(
            175, 180-stat_prosent[2]*hoyde-40, text=str(stat_prosent[2])+'%', anchor=N)
        cvs_karstat.create_text(175, 180, text='C - ' +
                                str(stat_kar[2]), anchor=S)

        cvs_karstat.create_rectangle(
            210, 160-stat_prosent[3]*hoyde, 240, 160, fill='yellow', outline='yellow')
        cvs_karstat.create_text(
            225, 180-stat_prosent[3]*hoyde-40, text=str(stat_prosent[3])+'%', anchor=N)
        cvs_karstat.create_text(225, 180, text='D - ' +
                                str(stat_kar[3]), anchor=S)

        cvs_karstat.create_rectangle(
            260, 160-stat_prosent[4]*hoyde, 290, 160, fill='yellow', outline='yellow')
        cvs_karstat.create_text(
            275, 180-stat_prosent[4]*hoyde-40, text=str(stat_prosent[4])+'%', anchor=N)
        cvs_karstat.create_text(275, 180, text='E - ' +
                                str(stat_kar[4]), anchor=S)

        cvs_karstat.create_rectangle(
            310, 160-stat_prosent[5]*hoyde, 340, 160, fill='red', outline='red')
        cvs_karstat.create_text(
            325, 180-stat_prosent[5]*hoyde-40, text=str(stat_prosent[5])+'%', anchor=N)
        cvs_karstat.create_text(325, 180, text='F - ' +
                                str(stat_kar[5]), anchor=S)

        cvs_karstat.create_line(50, 160, 350, 160, width=2)

        cvs_karstat.create_text(200, 375, text='Karakterer', anchor=N)

    def eksamen_ny():
        def ledige_rom(Event):
            nyEks_cursor = mindatabase.cursor()
            nyEks_cursor.execute("SELECT Romnr, Antallplasser "
                                "FROM Rom ")

            opptatt = []
            for i in tvw_eksamen.get_children():
                intermediary = tvw_eksamen.item(i)['values'][2]
                if dato.get() == intermediary:
                    opptatt += [tvw_eksamen.item(i)['values'][1]]

            rom_liste = ['(Velg rom)']
            row = nyEks_cursor.fetchone()
            while row != None:
                taken = False
                if len(opptatt) > 0:
                    for i in opptatt:
                        if i == row[0]:
                            taken = True
                if taken == False:
                    rom_liste += [row[0]+' ('+str(row[1])+' plasser)']
                    row = nyEks_cursor.fetchone()
                else:
                    row = nyEks_cursor.fetchone()

            nyEks_cursor.close()
            cBox_rom['values'] = rom_liste

        def velg_dato(event):
            if dato.get() == 'YYYY-MM-DD':
                ent_dato.delete(0, END)
                ent_dato['fg'] = 'black'

        def velg_dato_av(event):
            if dato.get() == '':
                ent_dato.insert(0, 'YYYY-MM-DD')
                ent_dato['fg'] = 'grey'

        def leggTil():
            if cBox_emne.get() != '(Velg emne)' and cBox_rom.get() != '(Velg rom)' and dato.get() != 'YYYY-MM-DD':
                # finn whitespace i romnr
                for i in range(4):
                    if cBox_rom.get()[i] == ' ':
                        siste = i

                nyEks_cursor = mindatabase.cursor()
                nyEks_cursor.execute("INSERT INTO Eksamen (Emnekode, Dato, Romnr) "
                                    "VALUES (%s, %s, %s)",
                                    (cBox_emne.get(), dato.get(), cBox_rom.get()[0:siste]))
                mindatabase.commit()
                nyEks_cursor.close()
                top_nyEksamen.destroy()
                til.set('')
                eksamen_sok()
            else:
                messagebox.showerror('Feil', 'Du må velge emne, rom og dato')

        top_nyEksamen = Toplevel()
        top_nyEksamen.title('Ny eksamen')

        nyEks_cursor = mindatabase.cursor()
        nyEks_cursor.execute("SELECT Emnekode "
                            "FROM Emne ")
        emne_liste = ['(Velg emne)']
        row = nyEks_cursor.fetchone()
        while row != None:
            emne_liste += row
            row = nyEks_cursor.fetchone()
        nyEks_cursor.close()

        cBox_emne = ttk.Combobox(
            top_nyEksamen, values=emne_liste, state='readonly')
        cBox_emne.grid(row=0, column=1, padx=5, pady=5, sticky=W)
        cBox_rom = ttk.Combobox(
            top_nyEksamen, values='(Velg Rom)', state='readonly')
        cBox_rom.grid(row=2, column=1, padx=5, pady=5, sticky=W)

        cBox_emne.current(0)
        cBox_rom.set('(Velg rom)')

        cBox_rom.bind('<Button>', ledige_rom)

        lbl_dato = Label(top_nyEksamen, text='Dato:')
        lbl_dato.grid(row=1, column=0, padx=5, pady=5, sticky=E)

        dato = StringVar()
        ent_dato = Entry(top_nyEksamen, textvariable=dato, fg='#b3b3b3')
        ent_dato.grid(row=1, column=1, padx=5, pady=5, sticky=W)
        ent_dato.insert(0, 'YYYY-MM-DD')

        ent_dato.bind('<FocusIn>', velg_dato)
        ent_dato.bind('<FocusOut>', velg_dato_av)

        btn_leggTil = Button(top_nyEksamen, text='Legg til', command=leggTil)
        btn_leggTil.grid(row=3, column=1, padx=5, pady=5, sticky=W)
        #btn_endre = Button(top_nyEksamen, text='Endre', command=endre_eksamen)
        #btn_endre.grid(row=4, column=1, padx=5, pady=5, sticky=W)
        btn_nyEks_lukk = Button(top_nyEksamen, text='Lukk', command=top_nyEksamen.destroy)
        btn_nyEks_lukk.grid(row=5, column=1, padx=5, pady=5, sticky=SE)

    def eksamen_endre():
        def ledige_rom(Event):
            nyEks_cursor = mindatabase.cursor()
            nyEks_cursor.execute("SELECT Romnr, Antallplasser "
                                "FROM Rom ")

            opptatt = []
            for i in tvw_eksamen.get_children():
                intermediary = tvw_eksamen.item(i)['values'][2]
                if dato.get() == intermediary:
                    opptatt += [tvw_eksamen.item(i)['values'][1]]


            rom_liste = [tvw_eksamen.item(tvw_eksamen.selection()[0])['values'][1]]
            row = nyEks_cursor.fetchone()
            while row != None:
                taken = False
                if len(opptatt) > 0:
                    for i in opptatt:
                        if i == row[0]:
                            taken = True
                if taken == False:
                    rom_liste += [row[0]+' ('+str(row[1])+' plasser)']
                    row = nyEks_cursor.fetchone()
                else:
                    row = nyEks_cursor.fetchone()

            nyEks_cursor.close()
            cBox_rom['values'] = rom_liste


        def leggTil():
            # finn whitespace i romnr
            for i in range(4):
                if cBox_rom.get()[i] == ' ':
                    siste = i

            nyEks_cursor = mindatabase.cursor()
            nyEks_cursor.execute("UPDATE Eksamen "
                                "SET Romnr = %s "
                                "WHERE Emnekode = %s AND Dato = %s", (cBox_rom.get()[0:siste], cBox_emne.get(), dato.get()))
            mindatabase.commit()
            nyEks_cursor.close()
            top_nyEksamen.destroy()
            eksamen_sok()


        

        top_nyEksamen = Toplevel()
        top_nyEksamen.title('Endre eksamen')

        nyEks_cursor = mindatabase.cursor()
        nyEks_cursor.execute("SELECT Emnekode "
                            "FROM Emne ")
        emne_liste = ['(Velg emne)']
        row = nyEks_cursor.fetchone()
        while row != None:
            emne_liste += row
            row = nyEks_cursor.fetchone()
        nyEks_cursor.close()

        cBox_emne = ttk.Combobox(
            top_nyEksamen, values=emne_liste, state='disabled')
        cBox_emne.grid(row=0, column=1, padx=5, pady=5, sticky=W)
        cBox_rom = ttk.Combobox(
            top_nyEksamen, values='(Velg Rom)', state='readonly')
        cBox_rom.grid(row=2, column=1, padx=5, pady=5, sticky=W)

        cBox_emne.set(tvw_eksamen.item(tvw_eksamen.selection()[0])['values'][0])
        cBox_rom.set(tvw_eksamen.item(tvw_eksamen.selection()[0])['values'][1])

        cBox_rom.bind('<Button>', ledige_rom)

        lbl_dato = Label(top_nyEksamen, text='Dato:')
        lbl_dato.grid(row=1, column=0, padx=5, pady=5, sticky=E)

        dato = StringVar()
        ent_dato = Entry(top_nyEksamen, textvariable=dato, state='readonly')
        ent_dato.grid(row=1, column=1, padx=5, pady=5, sticky=W)
        ent_dato.insert(0, 'YYYY-MM-DD')

        btn_leggTil = Button(top_nyEksamen, text='Endre', command=leggTil)
        btn_leggTil.grid(row=3, column=1, padx=5, pady=5, sticky=W)
        # btn_endre = Button(top_nyEksamen, text='Endre', command=endre_eksamen)
        # btn_endre.grid(row=4, column=1, padx=5, pady=5, sticky=W)
        btn_nyEks_lukk = Button(
            top_nyEksamen, text='Lukk', command=top_nyEksamen.destroy)
        btn_nyEks_lukk.grid(row=5, column=1, padx=5, pady=5, sticky=SE)

        dato.set(tvw_eksamen.item(tvw_eksamen.focus())['values'][2])

    def eksamen_slett():
        emne = tvw_eksamen.item(tvw_eksamen.selection())['values'][0]
        rom = tvw_eksamen.item(tvw_eksamen.selection())['values'][1]
        dato = tvw_eksamen.item(tvw_eksamen.selection())['values'][2]

        today_cursor = mindatabase.cursor()
        today_cursor.execute("SELECT CURRENT_DATE() AS today")
        today = today_cursor.fetchone()
        today = str(today[0])
        today_cursor.close()

        if dato >= today:
            usure = messagebox.showwarning(
                'Slett eksamen', 'Er du sikker på at du vil slette '+emne+' eksamen i rom '+rom+' den '+dato+'?')
            if usure == 'ok':
                eksSlett_cursor = mindatabase.cursor()
                eksSlett_cursor.execute("DELETE FROM eksamen "
                                        "WHERE Emnekode = %s "
                                        "AND Romnr = %s "
                                        "AND Dato = %s", (emne, rom, dato))
                mindatabase.commit()
                eksSlett_cursor.close()
                eksamen_sok()
        else:
            messagebox.showwarning(
                'Slett eksamen', 'Du kan ikke slette en eksamen som har vært')

    def radio_sok():
        if radio.get() == 0:
            ent_fra['state'] = 'normal'
            fra.set('')
            ent_til['state'] = 'normal'
            til.set('')
            btn_karStat.grid(row=9, column=3, padx=5, pady=4, columnspan=2)
            btn_reg.grid(row=10, column=3, padx=5, pady=4, columnspan=2)
            sep_tid.grid(row=11, column=3, columnspan=2,
                        sticky=EW, padx=5, pady=4)
            btn_ny.grid(row=12, column=3, padx=5, pady=4, columnspan=2)
            btn_endre.grid(row=13, column=3, padx=5, pady=4, columnspan=2)
            btn_slett.grid(row=14, column=3, padx=5, pady=4, columnspan=2)
        else:
            today_cursor = mindatabase.cursor()
            today_cursor.execute("SELECT CURRENT_DATE() AS today")
            today = today_cursor.fetchone()
            today = today[0]
            today_cursor.close()

            if radio.get() == 1:
                ent_fra['state'] = 'readonly'
                fra.set(today)
                ent_til['state'] = 'normal'
                til.set('')
                btn_karStat.grid_remove()
                btn_reg.grid_remove()
                sep_tid.grid_remove()
                btn_ny.grid(row=9, column=3, padx=5, pady=4, columnspan=2)
                btn_endre.grid(row=10, column=3, padx=5, pady=4, columnspan=2)
                btn_slett.grid(row=11, column=3, padx=5, pady=4, columnspan=2)
            else:
                ent_fra['state'] = 'normal'
                fra.set('')
                ent_til['state'] = 'readonly'
                til.set(today)
                sep_tid.grid_remove()
                btn_ny.grid_remove()
                btn_endre.grid_remove()
                btn_slett.grid_remove()
                btn_karStat.grid(row=9, column=3, padx=5, pady=4, columnspan=2)
                btn_reg.grid(row=10, column=3, padx=5, pady=4, columnspan=2)

        eksamen_sok()

    def eksamen_sok():
        tvw_eksamen.delete(*tvw_eksamen.get_children())
        eksamen_cursor = mindatabase.cursor()
        dat_fra = fra.get()
        dat_til = til.get()
        if dat_fra == '' or dat_til == '':
            query = ("SELECT MIN(Dato) as MinDato, MAX(Dato) as MaxDato "
                    "FROM Eksamen ")
            eksamen_cursor.execute(query)
            row = eksamen_cursor.fetchone()
            if dat_til != '':
                dat_fra = row[0]
                fra.set(dat_fra)
            else:
                if dat_fra != '':
                    dat_til = row[1]
                    til.set(dat_til)
                else:
                    dat_fra = row[0]
                    fra.set(dat_fra)
                    dat_til = row[1]
                    til.set(dat_til)

        query = ("SELECT Emnekode, RomNr, Dato "
                "FROM Eksamen "
                "WHERE Dato BETWEEN %s AND %s "
                "ORDER BY Dato DESC")
        eksamen_cursor.execute(query, (dat_fra, dat_til))
        row = eksamen_cursor.fetchone()
        tabell = []
        while row != None:
            tabell += [[row[0], row[1], row[2], '']]
            row = eksamen_cursor.fetchone()
        eksamen_cursor.close()

        # Finner eksamner med like datoer og romnr fra tabell
        for i in range(len(tabell)):
            for j in range(i+1, len(tabell)):
                if tabell[i][1] == tabell[j][1] and tabell[i][2] == tabell[j][2]:
                    tabell[i][3] = 'duplikat'
                    tabell[j][3] = 'duplikat'

        count = 0
        while count < len(tabell):
            if tabell[count][3] != 'duplikat':
                tvw_eksamen.insert('', index=count, text='', values=(
                    tabell[count][0], tabell[count][1], tabell[count][2]))
            else:
                tvw_eksamen.insert('', index=count, text='', values=(
                    tabell[count][0], tabell[count][1], tabell[count][2]), tag=('duplikat'))
            count += 1
        tvw_eksamen.tag_configure('duplikat', background='red')

    # definerer vindu
    top_eksamen = Toplevel(window)
    top_eksamen.title('Eksamensresultater')

    # definerer tabell
    scroll_eksamen = Scrollbar(top_eksamen, orient=VERTICAL)
    scroll_eksamen.grid(row=1, column=2, padx=(
        0, 5), pady=10, rowspan=15, sticky=NS)

    tvw_eksamen = ttk.Treeview(top_eksamen, columns=(
        'Emnekode', 'Rom', 'Dato'), yscrollcommand=scroll_eksamen.set, height=15)
    tvw_eksamen.column('#0', width=0, stretch=NO)
    tvw_eksamen.column('Emnekode', width=100)
    tvw_eksamen.column('Rom', width=100)
    tvw_eksamen.column('Dato', width=100)

    tvw_eksamen.heading('#0', text='')
    tvw_eksamen.heading('Emnekode', text='Emnekode')
    tvw_eksamen.heading('Rom', text='Rom')
    tvw_eksamen.heading('Dato', text='Dato')
    tvw_eksamen.grid(row=1, column=0, padx=(10, 0), pady=10,
                    rowspan=15, columnspan=2, sticky=NSEW)

    scroll_eksamen['command'] = tvw_eksamen.yview

    # definerer widgets
    lbl_eksamner = Label(top_eksamen, text='Eksamner:')
    lbl_eksamner.grid(row=0, column=0, padx=10, pady=(10, 0), sticky=W)
    lbl_duplikat = Label(top_eksamen, text='Duplikat', bg='red')
    lbl_duplikat.grid(row=0, column=1, padx=10, pady=(10, 0), sticky=W)
    lbl_periode = Label(top_eksamen, text='Periode:')
    lbl_periode.grid(row=0, column=3, padx=5, pady=4, columnspan=2, sticky=W)
    lbl_fra = Label(top_eksamen, text='Fra:')
    lbl_fra.grid(row=5, column=3, padx=(5, 0), pady=(4, 0), sticky=E)
    lbl_til = Label(top_eksamen, text='Til:')
    lbl_til.grid(row=6, column=3, padx=(5, 0), pady=(0, 4), sticky=E)

    fra = StringVar()
    ent_fra = Entry(top_eksamen, width=10, textvariable=fra)
    ent_fra.grid(row=5, column=4, padx=(0, 10), pady=4, sticky=W)
    til = StringVar()
    ent_til = Entry(top_eksamen, width=10, textvariable=til)
    ent_til.grid(row=6, column=4, padx=(0, 10), pady=4, sticky=W)

    btn_sok = Button(top_eksamen, text='Søk', command=eksamen_sok)
    btn_sok.grid(row=7, column=3, padx=5, pady=4, columnspan=2)
    btn_karStat = Button(
        top_eksamen, text='Karakterstatistikk', command=karstat)
    btn_karStat.grid(row=9, column=3, padx=5, pady=4, columnspan=2)
    btn_reg = Button(top_eksamen, text='Karakterer', command=kar_reg)
    btn_reg.grid(row=10, column=3, padx=5, pady=4, columnspan=2)
    btn_ny = Button(top_eksamen, text='Ny eksamen', command=eksamen_ny)
    btn_ny.grid(row=12, column=3, padx=5, pady=4, columnspan=2)
    btn_endre = Button(top_eksamen, text='Endre eksamen', command=eksamen_endre)
    btn_endre.grid(row=13, column=3, padx=5, pady=4, columnspan=2)
    btn_slett = Button(top_eksamen, text='Slett eksamen',
                        command=eksamen_slett)
    btn_slett.grid(row=14, column=3, padx=5, pady=4, columnspan=2)
    btn_lukk = Button(top_eksamen, text='Lukk', command=top_eksamen.destroy)
    btn_lukk.grid(row=15, column=4, padx=5, pady=(15, 5), sticky=SE)

    sep_sok = ttk.Separator(top_eksamen, orient=HORIZONTAL)
    sep_sok.grid(row=4, column=3, padx=10, pady=5, columnspan=2, sticky=EW)
    sep_radio = ttk.Separator(top_eksamen, orient=HORIZONTAL)
    sep_radio.grid(row=8, column=3, padx=5, pady=4, columnspan=2, sticky=EW)
    sep_tid = ttk.Separator(top_eksamen, orient=HORIZONTAL)
    sep_tid.grid(row=11, column=3, padx=10, pady=5, columnspan=2, sticky=EW)

    radio = IntVar()
    rd_alle = Radiobutton(top_eksamen, text='Alle eksamener',
                        variable=radio, value=0, command=radio_sok)
    rd_alle.grid(row=1, column=3, padx=5, columnspan=2, sticky=W)
    rd_fremtidige = Radiobutton(
        top_eksamen, text='Fremtidige eksamener', variable=radio, value=1, command=radio_sok)
    rd_fremtidige.grid(row=2, column=3, padx=5, columnspan=2, sticky=W)
    rd_tidligere = Radiobutton(
        top_eksamen, text='Tidligere eksamener', variable=radio, value=2, command=radio_sok)
    rd_tidligere.grid(row=3, column=3, padx=5, columnspan=2, sticky=W)

    eksamen_sok()


#Hent database
mindatabase = mysql.connector.connect(
    host='localhost', port=3306, user='Eksamenssjef', passwd='oblig2023', db='oblig2023')

#Hovedmenyvindu
window = Tk()
window.title('Eksamenshåndtering')

btn_studenter = Button(window, text='Studenter', command=studenter)
btn_studenter.grid(row=0, column=0, padx=15, pady=15, sticky=W)
btn_eksamen = Button(window, text='Eksamener', command=eksamner)
btn_eksamen.grid(row=1, column=0, padx=15, pady=15, sticky=W)
btn_avslutt = Button(window, text='Avslutt', command=window.destroy)
btn_avslutt.grid(row=2, column=1, padx=5, pady=5, sticky=SE)

window.mainloop()