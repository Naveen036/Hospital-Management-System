from flask import Flask, render_template, redirect, session, url_for, request, flash, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,date

app = Flask(__name__)
app.config['SECRET_KEY']="secretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hms.db'
db = SQLAlchemy(app)
adddiag = []
addmed = []
#bg-color = #33383D

# Database Start

class Userstore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50),unique=True)
    password = db.Column(db.String(80))
    role = db.Column(db.String(50))
    
    def __repr__(self):
        return 'User '+str(self.id)

class Patient(db.Model):
    pat_id = db.Column(db.Integer, primary_key=True)
    pat_ssn = db.Column(db.String(50),unique=True)
    pat_name = db.Column(db.String(100))
    pat_age = db.Column(db.Integer)
    pat_doa = db.Column(db.String(25))
    pat_bed_type = db.Column(db.String(100))
    pat_addr = db.Column(db.String(255))
    pat_city = db.Column(db.String(50))
    pat_state = db.Column(db.String(50))
    pat_status = db.Column(db.String(50))
    patdiag = db.relationship('Patientdiag',backref='Patient')
    patmed = db.relationship('Patientmed',backref='Patient')  
    
    def __repr__(self):
        return 'Patient '+str(self.pat_id)

class Medicine(db.Model):
    med_id = db.Column(db.Integer, primary_key=True)
    med_name = db.Column(db.String(100),unique=True)
    med_cost = db.Column(db.Integer)
    med_qty = db.Column(db.Integer)
    med_status = db.Column(db.String(50))
     
    def __repr__(self):
        return 'Medicine '+str(self.med_id)

class Diagnostics(db.Model):
    diag_id = db.Column(db.Integer, primary_key=True)
    diag_name = db.Column(db.String(100),unique=True)
    diag_cost = db.Column(db.Integer)
 
    def __repr__(self):
        return 'Diagnostic '+str(self.diag_id)

class Patientdiag(db.Model):
    patdiag_id = db.Column(db.Integer, primary_key = True)
    pat_id = db.Column(db.Integer, db.ForeignKey('patient.pat_id'))
    patdiag_name = db.Column(db.String(50))
    patdiag_cost = db.Column(db.Integer)
    

    def __repr__(self):
        return 'PatientDiag '+str(self.patdiag_id)

class Patientmed(db.Model):
    patmed_id = db.Column(db.Integer, primary_key = True)
    pat_id = db.Column(db.Integer, db.ForeignKey('patient.pat_id'))
    patmed_name = db.Column(db.String(50))
    patmed_cost = db.Column(db.Integer)
    patmed_qty = db.Column(db.Integer)
    patmed_amt = db.Column(db.Integer)

    def __repr__(self):
        return 'PatientMed '+str(self.patmed_id)

# Database End

# Login and Dashboard Start

@app.route("/",methods = ['GET','POST'])
@app.route("/login",methods = ['GET','POST'])
def login():
    if request.method =='POST':
        username_form = request.form['username']
        password_form = request.form['password']
        user = Userstore.query.filter_by(username = username_form).first()
    
        if user:
            if password_form == user.password:
                session['user'] = user.role
                session['logged_in'] = True
                return redirect(url_for("dashboard"))
            else:
                flash("Incorrect Password","danger")
                return redirect("/")
        else:
            flash("User doesnt exist","danger")
            return redirect("/") 

    return render_template("login.html")

@app.route('/logout')
def logout():
    if session['logged_in']==True:
        session['logged_in']= False
        session['user']=None
        print(session)
        return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))
    

@app.route("/dashboard")
def dashboard():
    if session['logged_in']==True:
        return render_template("dashboard.html",name = session['user'])
    else:
        return redirect(url_for("login"))

@app.errorhandler(KeyError)
def keyError(e):
    flash("Login Required","danger")
    return redirect('/login')

# Login and Dashboard End

# Cashier Operations Start


@app.route("/dashboard/addPatient",methods=['GET','POST'])
def addPatient():
    if session['logged_in']==True:
        if request.method=='POST':
            ssn = request.form['patient_ssn']
            name = request.form['patient_name']
            age = request.form['age']
            doa = request.form['doa']
            bed_type = request.form['bed_type']
            address = request.form['address']
            state = request.form['patient_state']
            city = request.form['patient_city']
            r = Patient.query.filter_by(pat_ssn = ssn).first()
            print(r)
            if r==None:
                result = Patient(pat_ssn=ssn, pat_name=name, pat_age=age, pat_doa=doa, pat_bed_type=bed_type, pat_addr=address, pat_city=city, pat_state=state, pat_status='active')
                db.session.add(result)
                db.session.commit()
                flash("Patient added successfully","success")
                return render_template("add_patient.html")
            else:
                flash("SSN id already exists","danger")
                return render_template("add_patient.html")
        else:
            return render_template("add_patient.html")
    else:
        return redirect(url_for("login"))

@app.route("/dashboard/editPatient", methods=['GET','POST'])
def editPatient():
    if session['logged_in']==True:
        if request.method=='POST':
            id = request.form['patient_id']
            patients = Patient.query.filter_by(pat_id = id).first()
            if patients == None:
                flash("Invalid Patient Id","danger")
                return render_template("edit_patient.html")
            else:
                return render_template("edit_patient.html",p=patients)
        else:
            return render_template("edit_patient.html")     
    else:
        return redirect(url_for("login"))

@app.route("/dashboard/patientEdit",methods=['POST'])
def patientEdit():
    if session['logged_in']==True:
        id = request.form['pid']
        ssn = request.form['patient_ssn']
        name = request.form['patient_name']
        age = request.form['age']
        doa = request.form['doa']
        bed_type = request.form['bed_type']
        address = request.form['address']
        state = request.form['state']
        city = request.form['city']
        status = request.form['status']

        update_patient = Patient.query.filter_by(pat_id = id).first()

        update_patient.pat_ssn = ssn
        update_patient.pat_name = name
        update_patient.pat_age = age
        update_patient.pat_doa = doa
        update_patient.pat_bed_type = bed_type
        update_patient.pat_addr = address
        update_patient.pat_city = city
        update_patient.pat_state = state
        update_patient.pat_status = status
            
        db.session.commit()
        flash("Patient Updated Successfully","success")
        return redirect(url_for("editPatient"))
        
    else:
        return redirect(url_for("login"))


@app.route("/dashboard/deletePatient",methods=['GET','POST'])
def deletePatient():
    if session['logged_in']==True:
        if request.method=='POST':
            id = request.form['patient_id']
            patients = Patient.query.filter_by(pat_id = id).first()
            if patients == None:
                flash("Invalid Patient Id","danger")
                return render_template("delete_patient.html")
            else:
                return render_template("delete_patient.html",p=patients)
        else:
            return render_template("delete_patient.html")     
    else:
        return redirect(url_for("login"))

@app.route("/dashboard/patientDelete",methods=['POST'])
def patientDelete():
    if session['logged_in']==True:
        ssn = request.form['patient_ssn']
        patient = Patient.query.filter_by(pat_ssn = ssn).first()
        db.session.delete(patient)
        db.session.commit()
        flash("Patient Deleted Successfully","success")
        return redirect(url_for("deletePatient"))
        
    else:
        return redirect(url_for("login"))

@app.route("/dashboard/viewPatient")
def viewPatient():
    if session['logged_in']==True:
        patients = Patient.query.all()
        if patients == None:
            flash("No Patients added","danger")
            return render_template("view_patient.html")
        else:
            return render_template("view_patient.html",patients=patients)
    else:
        return redirect(url_for("login"))

@app.route("/dashboard/billing",methods=['GET','POST'])
def billing():
    if session['logged_in']==True:
        if request.method=='POST':
            session['patient_id']=None
            id = request.form['patient_id']
            session['patient_id']=id
            patient = Patient.query.filter_by(pat_id = id).first()
            rt = mt = dt = 0
            if patient == None:
                flash("Invalid Patient Id","danger")
                return render_template("billing.html")
            else:
                patmed = Patientmed.query.filter_by(pat_id = id).all()
                patdiag = Patientdiag.query.filter_by(pat_id = id).all()
                for pm in patmed:
                    mt = mt + pm.patmed_amt
                for pd in patdiag:
                    dt = dt + pd.patdiag_cost
                dod = date.today()
                doa = datetime.strptime(patient.pat_doa, '%Y-%m-%d').date()
                nod = (dod-doa).days
                if patient.pat_bed_type == "General ward":
                    rt = nod*2000
                elif patient.pat_bed_type == "Semi sharing":
                    rt = nod*4000
                elif patient.pat_bed_type == "Single Room":
                    rt = nod*8000
                print(rt,mt,dt)
                return render_template("billing.html",p=patient,patmed = patmed, patdiag = patdiag, dod=dod,nod=nod,rt=rt,mt=mt,dt=dt)
        
        else:
            return render_template("billing.html")
    else:
        return redirect(url_for("login"))

@app.route("/dashboard/billingDone")
def billingDone():
    if session["logged_in"]==True:
        patient = Patient.query.filter_by(pat_id = session['patient_id']).first()
        patmed = Patientmed.query.filter_by(pat_id = session['patient_id']).all()
        patdiag = Patientdiag.query.filter_by(pat_id = session['patient_id']).all()
        patient.pat_status = 'Discharged'
        for pm in patmed:
            db.session.delete(pm)
        for pd in patdiag:
            db.session.delete(pd)
        db.session.commit()
        flash("Payment successful","success")
        return redirect(url_for("billing"))
    else:
        return redirect(url_for("login"))


@app.route("/dashboard/patientSearch",methods=['GET','POST'])
def patientSearch():
    if session['logged_in']==True:
        if request.method=='POST':
            id = request.form['patient_id']
            patients = Patient.query.filter_by(pat_id = id).first()
            if patients == None:
                flash("No Patients added","danger")
                return render_template("dashboard.html")
            else:
                return render_template("dashboard.html",p=patients)
        else:
            return redirect(url_for("dashboard"))     
    else:
        return redirect(url_for("login"))

# Cashier Operations End

# Pharmasist Operations Start

@app.route("/dashboard/addMedicine",methods=['GET','POST'])
def addMedicine():
    if session['logged_in']==True:
        if request.method=='POST':
            mname = request.form['mname']
            mcost = request.form['mcost']
            mqty = request.form['mqty']
            if mqty==0:
                mstatus = 'Not Available'
            else:
                mstatus = 'Available'

            medicine = Medicine.query.filter_by(med_name = mname).first()
            
            if medicine==None:
                result = Medicine(med_name = mname, med_cost= mcost, med_qty=mqty, med_status=mstatus)
                db.session.add(result)
                db.session.commit()
                flash("Medicine added successfully","success")
                return redirect(url_for("addMedicine"))
            else:
                flash("Medicine already exists","danger")
                return redirect(url_for("addMedicine"))
        else:
            return render_template("add_medicine.html")
    else:
        return redirect(url_for("login"))

@app.route("/dashboard/updateMedicine", methods=['GET','POST'])
def updateMedicine():
    if session['logged_in']==True:
        if request.method=='POST':
            med_id = request.form['medicine_id']
            medicine = Medicine.query.filter_by(med_id = med_id).first()
            if medicine == None:
                flash("Invalid Medicine name","danger")
                return render_template("update_medicine.html")
            else:
                return render_template("update_medicine.html",m=medicine)
        else:
            return render_template("update_medicine.html")     
    else:
        return redirect(url_for("login"))

@app.route("/dashboard/medicineUpdate",methods=['POST'])
def medicineUpdate():
    if session['logged_in']==True:
        id = request.form['mid']
        med_name = request.form['mname']
        med_cost = request.form['mcost']
        med_qty =int(request.form['mqty'])
        if med_qty==0:
            med_status = 'Not Available'
        else:
            med_status = 'Available'

        update_medicine = Medicine.query.filter_by(med_id = id).first()

        update_medicine.med_name = med_name
        update_medicine.med_cost = med_cost
        update_medicine.med_qty = med_qty
        update_medicine.med_status = med_status
           
        db.session.commit()
        flash("Medicine Updated Successfully","success")
        return redirect(url_for("updateMedicine"))
        
    else:
        return redirect(url_for("login"))


@app.route("/dashboard/viewMedicine")
def viewMedicine():
    if session['logged_in']==True:
        medicines = Medicine.query.all()
        if medicines == None:
            flash("No Medicines added","danger")
            return render_template("view_medicine.html")
        else:
            return render_template("view_medicine.html",medicines=medicines)
    else:
        return redirect(url_for("login"))

@app.route("/dashboard/issueMedicine",methods=['GET','POST'])
def issueMedicine():
    if session['logged_in']==True:
        if request.method=='POST':
            session['patient_id']=None
            addmed.clear()
            id = request.form['patient_id']
            session['patient_id'] = request.form['patient_id']
            patients = Patient.query.filter_by(pat_id = id).first()
            patmed = Patientmed.query.filter_by(pat_id = id).all()
            allmed = Medicine.query.all()
            if patients == None:
                flash("No Patients added","danger")
                return render_template("issue_medicines.html")
            else:
                return render_template("issue_medicines.html",p=patients, allmed= allmed, patmed=patmed)
        else:
            return render_template("issue_medicines.html")
    else:
        return redirect(url_for("login"))

@app.route("/dashboard/issueMedicine/add",methods=['POST'])
def issueMedicineAdd():
    if session['logged_in']==True:
        med_name = request.form['med_name']
        med_qty = int(request.form['med_qty'])
        medunit={}
        medunit['name'] = med_name
        medunit['qty'] = med_qty
        patients = Patient.query.filter_by(pat_id = session['patient_id']).first()
        patmed = Patientmed.query.filter_by(pat_id = session['patient_id']).all()
        allmed= Medicine.query.all()
        medicine = Medicine.query.filter_by(med_name = med_name).first()
        c=0
        for m in addmed:
            if m['name'] == med_name:
                c=1 
                break           
                    
        if c!=1:
            if medicine.med_qty >= med_qty: 
                medunit['cost'] = medicine.med_cost
                medunit['amt'] = med_qty*medicine.med_cost
                addmed.append(medunit)
                print(addmed)
                return render_template('issue_medicines.html',medicines = addmed, p = patients,allmed = allmed,patmed=patmed  )
            else:
                flash("Quantity Exceeded","danger")
                return render_template('issue_medicines.html',medicines = addmed, p = patients,allmed = allmed, patmed=patmed  )

        else:
            flash("Already in list","danger")
            print(addmed)
            return render_template('issue_medicines.html',medicines = addmed, p = patients,allmed = allmed, patmed=patmed  )
            
    else:
        return redirect(url_for("login"))


@app.route('/dashboard/issueMedicine/issueMedDone',methods=['POST','GET'])
def issueMedDone():
    if session['logged_in']==True:
        for m in addmed:
            patmed_name = m['name']
            patmed_cost = m['cost']
            patmed_qty = m['qty']
            patmed_amt = m['amt']
            medicine = Medicine.query.filter_by(med_name = patmed_name).first()
            medicine.med_qty = medicine.med_qty - patmed_qty
            if medicine.med_qty == 0:
                medicine.med_status = "Not Availabale"
            db.session.add(Patientmed(pat_id = session['patient_id'],patmed_name=patmed_name,patmed_cost = patmed_cost,patmed_qty=patmed_qty,patmed_amt=patmed_amt))
            db.session.commit()
        addmed.clear()
        session['patient_id']=None
        flash("Medicines issued successfully!!","success")
        return redirect(url_for("issueMedicine"))
    else:
        return redirect(url_for("login"))

@app.route("/dashboard/patMedSearch",methods=["POST"])
def patMedSearch():
    if session["logged_in"]==True:
        id = request.form['patient_id']
        patmed = Patientmed.query.filter_by(pat_id = id).all()
        print(patmed)
        if len(patmed)==0:
                if Patient.query.filter_by(pat_id = id).first():
                    flash("No Records for given ID","danger")
                    return render_template("dashboard.html")
                else:
                    flash("Invalid Patient Id ","danger")
                    return render_template("dashboard.html")
        else:
            return render_template("dashboard.html",patmed=patmed)
        
    else:
        return redirect(url_for("login"))

# Pharmasist Operations End 

# Diagnostic Operation Start

@app.route("/dashboard/addDiagnostic",methods=['GET','POST'])
def addDiagnostic():
    if session['logged_in']==True:
        if request.method=='POST':
            dname = request.form['dname']
            dcost = request.form['dcost']
            
            diagnostic = Diagnostics.query.filter_by(diag_name = dname).first()
            
            if diagnostic==None:
                result = Diagnostics(diag_name = dname, diag_cost= dcost)
                db.session.add(result)
                db.session.commit()
                flash("Diagnostic Test added successfully","success")
                return redirect(url_for("addDiagnostic"))
            else:
                flash("Diagnostic Test already exists","danger")
                return redirect(url_for("addDiagnostic"))
        else:
            return render_template("add_diagnostic.html")
    else:
        return redirect(url_for("login"))

@app.route("/dashboard/updateDiagnostic", methods=['GET','POST'])
def updateDiagnostic():
    if session['logged_in']==True:
        if request.method=='POST':
            diag_id = request.form['diagnostic_id']
            diagnostic = Diagnostics.query.filter_by(diag_id = diag_id).first()
            if diagnostic == None:
                flash("Invalid Diagnostic id","danger")
                return render_template("update_diagnostic.html")
            else:
                return render_template("update_diagnostic.html",d=diagnostic)
        else:
            return render_template("update_diagnostic.html")     
    else:
        return redirect(url_for("login"))


@app.route("/dashboard/diagnosticUpdate",methods=['POST'])
def diagnosticUpdate():
    if session['logged_in']==True:
        id = request.form['did']
        diag_name = request.form['dname']
        diag_cost = request.form['dcost']
        
        update_diagnostic = Diagnostics.query.filter_by(diag_id = id).first()

        update_diagnostic.diag_name = diag_name
        update_diagnostic.diag_cost = diag_cost
           
        db.session.commit()
        flash("Diagnostic Updated Successfully","success")
        return redirect(url_for("updateDiagnostic"))
        
    else:
        return redirect(url_for("login"))

@app.route("/dashboard/viewDiagnostic")
def viewDiagnostic():
    if session['logged_in']==True:
        diagnostics = Diagnostics.query.all()
        if diagnostics == None:
            flash("No Diagnostic tests added","danger")
            return render_template("view_diagnostic.html")
        else:
            return render_template("view_diagnostic.html",diagnostics=diagnostics)
    else:
        return redirect(url_for("login"))

@app.route("/dashboard/issueDiagnostic",methods=['GET','POST'])
def issueDiagnostic():
    if session['logged_in']==True:
        if request.method=='POST':
            session['patient_id']=None
            adddiag.clear()
            id = request.form['patient_id']
            session['patient_id'] = request.form['patient_id']
            patients = Patient.query.filter_by(pat_id = id).first()
            patdiag = Patientdiag.query.filter_by(pat_id = id).all()
            alldiag = Diagnostics.query.all()
            if patients == None:
                flash("No Patients added","danger")
                return render_template("issue_diagnostics.html")
            else:
                return render_template("issue_diagnostics.html",p=patients,alldiag= alldiag,patdiag=patdiag)
        else:
            return render_template("issue_diagnostics.html")
    else:
        return redirect(url_for("login"))

@app.route("/dashboard/issueDiagnostic/add",methods=['POST'])
def issueDiagnosticAdd():
    if session['logged_in']==True:
        diag_name = request.form['diag_name']
        diagnostic = Diagnostics.query.filter_by(diag_name = diag_name).first()
        patdiag = Patientdiag.query.filter_by(pat_id = session['patient_id']).all()
        c=0
        for d in adddiag:
            if d.diag_id == diagnostic.diag_id:
                c=1 
                break           
                    
        if c!=1:
            adddiag.append(diagnostic)
            alldiag = Diagnostics.query.all()
            print(adddiag)
            patients = Patient.query.filter_by(pat_id = session['patient_id']).first()
            return render_template('issue_diagnostics.html',diagnostic = adddiag, p = patients,alldiag= alldiag,patdiag=patdiag  )
        else:
            flash("Already in list","danger")
            alldiag = Diagnostics.query.all()
            print(adddiag)
            patients = Patient.query.filter_by(pat_id = session['patient_id']).first()
            return render_template('issue_diagnostics.html',diagnostic = adddiag, p = patients,alldiag= alldiag,patdiag=patdiag  )
            
            
    else:
        return redirect(url_for("login"))

@app.route('/dashboard/issueDiagnostic/issueDiagDone',methods=['POST','GET'])
def issueDiagDone():
    if session['logged_in']==True:
        for d in adddiag:
            diag_name = d.diag_name
            diag_cost = d.diag_cost
            db.session.add(Patientdiag(pat_id = session['patient_id'],patdiag_name=diag_name,patdiag_cost = diag_cost))
            db.session.commit()
        adddiag.clear()
        session['patient_id']=None
        flash("Diagnostics issued successfully!!","success")
        return redirect(url_for("issueDiagnostic"))
    else:
        return redirect(url_for("login"))


@app.route("/dashboard/patDiagSearch",methods=['GET','POST'])
def patDiagSearch():
    if session['logged_in']==True:
        if request.method=='POST':
            id = request.form['patient_id']
            print(id)
            patdiag = Patientdiag.query.filter_by(pat_id = id).all()
            print(patdiag)
            if len(patdiag)==0:
                if Patient.query.filter_by(pat_id = id).first():
                    flash("No Records for given ID","danger")
                    return render_template("dashboard.html")
                else:
                    flash("Invalid Patient Id ","danger")
                    return render_template("dashboard.html")
            else:
                return render_template("dashboard.html",patdiag=patdiag)
            
        else:
            return redirect(url_for("dashboard"))     
    else:
        return redirect(url_for("login"))


# Diagnostic Operation End     

if __name__=="__main__":
    app.run(debug=True)