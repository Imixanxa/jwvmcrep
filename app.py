from codecs import BufferedIncrementalDecoder
from typing import List, Type
from flask import Flask, render_template, request, redirect, url_for, flash
import flask
from flask.wrappers import Request
from flask_mysqldb import MySQL
import mysql.connector
import pandas as pd
from mysql.connector import errorcode
import re
from datetime import datetime, date, timedelta, time
from tkinter import *
from tkcalendar import *
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta, MO
import keyword
app=Flask('__name__')

cnx = mysql.connector.connect(user='ejemplo', password='ejemplo',
                              host='127.0.0.1',
                              database='isidro')

try:
  cnx = mysql.connector.connect(user='ejemplo',
                                database='isidro')

except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database escuela does not exist")
  else:
    print(err)

app.secret_key = 'imixanxa'

@app.route('/')
def Index():
  return render_template('menuvmc.html')

@app.route('/asignaciones', methods=['POST','GET'])
def asignaciones():
  if request.method=='POST':
     period = request.form['periodo_m']

     if not period :
         flash('Error. you must enter period beforehand')
         return render_template('asignacionesfm.html' )

     indiceg = period.find('-')
     anio = period [0:indiceg]
     mes = period [indiceg+1:len( period )] 
             
     topics = request.form['tipo_a']
     if not topics:
         sqlplan = """ select * 
         FROM programamensual 
         WHERE actualizadofecha is null and pgmano = %s and pgmmes = %s """ 
         sqlvalue = (anio, mes)
         csr = cnx.cursor(buffered = True)
         csr.execute(sqlplan, (sqlvalue))                                               
         rcdplan=csr.fetchall()
         if not rcdplan:
            flash(f'no hay registros en la base plan maestro, {anio}')
            return redirect ( url_for ('asignaciones')  )
         return redirect ( url_for ('topicos', anio=anio, mes=mes, topics=" " ) )
     else:
         topico= '%'+topics+'%'
         sqlplan = """ select * 
         FROM programamensual 
         WHERE actualizadofecha is null and pgmano = %s and pgmmes = %s and pgmtipoasig like %s """ 
         sqlvalue = (anio, mes, topico)
         csr = cnx.cursor(buffered = True)
         csr.execute(sqlplan, (sqlvalue))                                               
         rcdplan=csr.fetchall()
         if not rcdplan:
            flash(f'no hay registros en la base plan maestro, con ese topico, {topics}')
            return redirect ( url_for ('asignaciones')  )
         for rcdplans in rcdplan:
            if re.search(topics,( rcdplans[8] )):
                return redirect ( url_for ('topicos', anio=anio, mes=mes, topics=topics ) )
         flash(f'error en el topico, {topics}')
         return redirect ( url_for ('asignaciones')  )

  else:
     mydate = datetime.now()
     anolargo=str(mydate.year)
     mescorto=mydate.strftime("%B") 
     periodo=mescorto+'    '+anolargo
     return render_template('asignacionesfm.html')

@app.route('/topicos/ <anio> <mes> <topics> ', methods=['GET', 'POST'])
def topicos(anio, mes, topics ):
    if not topics :
        sqlpgm = """SELECT * 
        FROM programamensual 
        WHERE actualizadofecha is null and pgmano = %s and pgmmes = %s """
        valpgm = (anio, mes)
        inx=cnx.cursor(buffered=True)
        inx.execute(sqlpgm,valpgm)
        rcdplan=inx.fetchall()
        if not rcdplan :
            flash(f'error, no hay anio / mes / { anio }')
            return redirect ( url_for ('asignaciones')  )
        print('empty',' ',rcdplan)

        return render_template('topicoreadfm.html', contacts = rcdplan, year=anio, month=mes, topics=" " )
    else:
        topico='%'+topics+'%'
        sqlpgm = """SELECT * 
        FROM programamensual 
        WHERE actualizadofecha is null and pgmano = %s and pgmmes = %s and pgmtipoasig like %s """
        valpgm = (anio, mes, topico)
        inx=cnx.cursor(buffered=True)
        inx.execute(sqlpgm,valpgm)
        rcdplan=inx.fetchall()
        if not rcdplan :
            flash(f'error, no hay anio / mes / topico en el plan maestro, {topics}')
            return redirect ( url_for ('asignaciones')  )
        print('full',' ',rcdplan)
        return render_template('topicoreadfm.html', contacts = rcdplan, year=anio, month=mes, topics=topics )


@app.route('/topico_read/<idplan>', methods=['POST','GET'])
def topico_read(idplan):
    pgmid_pm=idplan
    inx=cnx.cursor(buffered = True)
    sql_pgm = """select * 
    FROM programamensual 
    WHERE pgmid_pm = %s """
    inx.execute(sql_pgm,(pgmid_pm,))
    rcdplan = inx.fetchone()

    if not rcdplan :
        flash(f'no hay plan maestro, {pgmid_pm}')
        return redirect ( url_for ('index') )

    if request.method == 'POST':
        periodo_doble = request.form['periodo_m']
        if not periodo_doble :
            flash('Error. you must enter period previously')
            return render_template('subtopicosfm.html', pgmid = pgmid_pm,
                                  semanai = (rcdplan[6]), semanaf = (rcdplan[7]) , topics = (rcdplan[8]) )
        indiceg = periodo_doble.find('-')
        anio = periodo_doble [0:indiceg]
        mes = periodo_doble [indiceg+1:len( periodo_doble )] 
        name_student = request.form['name']
        if not name_student :
            sqlvalue=(anio, mes)
            sqlcrta = """ select * 
            FROM msthistori a
            INNER JOIN mststudent b
            ON a.hstid = b.mstid 
            where hstyear >= %s and hstmonth >= %s  """
            csr = cnx.cursor(buffered=True)
            csr.execute(sqlcrta,(sqlvalue))
            rcdhsta = csr.fetchall()

            sqlcrtb = """ select * 
            FROM msthistori a
            INNER JOIN mststudent b
            ON a.hstid2 = b.mstid
            where hstyear >= %s and hstmonth >= %s """
            csr = cnx.cursor(buffered=True)
            csr.execute(sqlcrtb,(sqlvalue))
            rcdhstb = csr.fetchall()

            if not rcdhstb :
                flash(f'error, review historical information of student')
                return render_template('subtopicosfm.html', pgmid = pgmid_pm,
                                      semanai = (rcdplan[6]), semanaf = (rcdplan[7]) , topics = (rcdplan[8]) )

            if (re.search('Lectura',( rcdplan[8] )) or re.search('Video',( rcdplan[8] )) or re.search('Discurso',( rcdplan[8] ))):
                return redirect ( url_for ('topico_lectura', pgmid = pgmid_pm, period=periodo_doble, 
                                        name_student=" " ) )
            else: 
                return redirect (url_for('topico_revisita',  planid=pgmid_pm, periodo = periodo_doble, 
                                        name_student = " ") )
        else:
            nombre='%'+name_student+'%'
            sqlvalue=(anio, mes, nombre, nombre )
            sqlcrta = """ select * 
            FROM msthistori a
            INNER JOIN mststudent b
            ON a.hstid = b.mstid 
            where hstyear >= %s and hstmonth >= %s and (hstname like %s or hstname2 like %s) """
            csr = cnx.cursor(buffered=True)
            csr.execute(sqlcrta,(sqlvalue))
            rcdhsta = csr.fetchall()

            sqlcrtb = """ select * 
            FROM msthistori a
            INNER JOIN mststudent b
            ON a.hstid2 = b.mstid
            where hstyear >= %s and hstmonth >= %s and (hstname2 like %s or hstname like %s)"""
            csr = cnx.cursor(buffered=True)
            csr.execute(sqlcrtb,(sqlvalue))
            rcdhstb = csr.fetchall()
        if not rcdhsta :
            flash(f'error4, review historical information of, {name_student}')
            return render_template('subtopicosfm.html', pgmid = pgmid_pm,
                                  semanai = (rcdplan[6]), semanaf = (rcdplan[7]) , topics = (rcdplan[8]) )
        namestudent='%'+ name_student + '%'
        sqltest="""select mstgenero as genero from mststudent where mstname like %s """
        inx=cnx.cursor(buffered=True)
        inx.execute(sqltest,(namestudent,))
        rcdtestmst = inx.fetchall()
        if not rcdtestmst:
            flash(f'error5, review historical information of, {name_student}')
            return render_template('subtopicosfm.html', pgmid = pgmid_pm,
            semanai = (rcdplan[6]), semanaf = (rcdplan[7]) , topics = (rcdplan[8]) )


        if (re.search('Lectura',( rcdplan[8] )) or re.search('Video',( rcdplan[8] )) or re.search('Discurso',( rcdplan[8] ))):
            for rcdtest in rcdtestmst:
                rcdtestmstchr=str( rcdtest )
                if (re.search('MASCULINO', rcdtestmstchr ) ):
                    continue
                else:
                    flash(f'error2, review historical information of gender, {name_student}')
                    return render_template('subtopicosfm.html', pgmid = pgmid_pm,
                    semanai = (rcdplan[6]), semanaf = (rcdplan[7]) , topics = (rcdplan[8]) )
            return redirect ( url_for ('topico_lectura', pgmid = pgmid_pm, period=periodo_doble, 
                                        name_student=name_student ) )
        else: 
            return redirect (url_for('topico_revisita',  planid=pgmid_pm, periodo = periodo_doble, 
                                    name_student = name_student) )
    else:
        # regresa a topico_read
        return render_template('subtopicosfm.html', pgmid=pgmid_pm, semanai = (rcdplan[6]), 
                               semanaf = (rcdplan[7]) , topics = (rcdplan[8]) )

@app.route('/topico_revisita/ <planid> <periodo> <name_student>', methods=['GET','POST'])
def topico_revisita(planid, periodo, name_student):
  if request.method=='GET':
    print('ns'+name_student+'ns')
    sql_pgm = """select * 
    FROM programamensual 
    WHERE pgmid_pm = %s """
    inx=cnx.cursor(buffered = True)
    inx.execute(sql_pgm,(planid,))
    rcdplan = inx.fetchone()

    indiceg = periodo.find('-')
    anio = int(periodo[0:indiceg])
    mes = int(periodo[indiceg+1:len(periodo)] )
    valpgm = (anio, mes)
    if name_student == " ":
          try:
            sqlsql = """ drop table if exists tablehstp"""
            inx=cnx.cursor(buffered=True)
            inx.execute(sqlsql)
            cnx.commit()
            sqlcrt = """ create table tablehstp as
            SELECT mstid, hstyear, hstmonth, hstname, hstid2, hstname2, hstasig, mstgenero, mststatus 
            FROM msthistori a, mststudent b 
            WHERE a.hstid=b.mstid and hstyear>=%s and hstmonth>=%s"""
            inx=cnx.cursor(buffered=True)
            inx.execute(sqlcrt, valpgm)
            cnx.commit()
          except:
            sqlcrt = """ create table tablehstp as
            SELECT mstid, hstyear, hstmonth, hstname, hstid2, hstname2, hstasig, mstgenero, mststatus 
            FROM msthistori a, mststudent b 
            WHERE a.hstid=b.mstid and hstyear>=%s and hstmonth>=%s"""
            inx=cnx.cursor(buffered=True)
            inx.execute(sqlcrt, valpgm)
            cnx.commit()
          try:
            sqlsql = """ drop table if exists tablehsta"""
            inx=cnx.cursor(buffered=True)
            inx.execute(sqlsql)
            cnx.commit()
            sqlcrt = """ create table tablehsta as
            SELECT hstyear, hstmonth, hstid2, hstname2 
            FROM msthistori a, mststudent b 
            WHERE a.hstid2=b.mstid and hstyear>=%s and hstmonth>=%s"""
            inx=cnx.cursor(buffered=True)
            inx.execute(sqlcrt, valpgm)
            cnx.commit()
          except:
            sqlcrt = """ create table tablehsta as
            SELECT hstyear, hstmonth, hstid2, hstname2 
            FROM msthistori a, mststudent b 
            WHERE a.hstid2=b.mstid and hstyear>=%s and hstmonth>=%s """
            inx=cnx.cursor(buffered=True)
            inx.execute(sqlcrt, valpgm)
            cnx.commit()

          sqlpgm = """SELECT distinct p.mstid, p.hstyear, p.hstmonth, p.hstname, p.hstid2, p.hstname2, p.hstasig, p.mstgenero, p.mststatus 
          FROM tablehstp p, tablehsta b 
          WHERE p.hstid2=b.hstid2 and p.hstyear>=%s and p.hstmonth>=%s
          ORDER BY p.hstname, p.hstname2, p.hstyear, p.hstmonth"""
          inx=cnx.cursor(buffered=True)
          inx.execute(sqlpgm,valpgm)
          rcd_stu_hst_all=inx.fetchall()
    else:
        name_t_a='%'+name_student+'%'
        valpgm = (anio, mes, name_t_a, name_t_a )
        sqlpgm = """SELECT mstid, hstyear, hstmonth, hstname, hstid2, hstname2, hstasig, mstgenero, mststatus 
        FROM msthistori a, mststudent b 
        WHERE a.hstid=b.mstid and hstyear>=%s and hstmonth>=%s and (hstname like %s or hstname2 like %s)
        ORDER BY hstname, hstname2, hstyear, hstmonth"""
        inx=cnx.cursor(buffered=True)
        inx.execute(sqlpgm,valpgm)
        rcd_stu_hst_all=inx.fetchall()
    if not rcd_stu_hst_all:
        return render_template('subtopicosfm.html', pgmid=planid, semanai = (rcdplan[6]), 
                               semanaf = (rcdplan[7]) , topics = (rcdplan[8]) )
    return render_template('topico_revisitafm.html', students = rcd_stu_hst_all, pgmid=planid,
                        semanai = (rcdplan[6]), semanaf = (rcdplan[7]) , topics= (rcdplan[8]) )
  else:
    pass   

@app.route('/topico_lectura/<pgmid> <period> <name_student>', methods=['GET','POST'])
def topico_lectura(pgmid, period, name_student):
  if request.method == 'GET' :
      sexolower='%masculino%'
      sexoupper='%MASCULINO%'
      censurado='CENSURADO'
      expulsado='EXPULSADO'
      indiceg = period.find('-')
      anio = int(period[0:indiceg])
      mes = int(period[indiceg+1:len(period)] )
      stmtsql= """select * from programamensual where pgmid_pm = %s """
      inx=cnx.cursor(buffered=True)
      inx.execute(stmtsql,(pgmid,))
      rcdplan=inx.fetchone()


      if not name_student:
        sqlpgm = """select mstid, hstyear, hstmonth, hstname, hstid2, hstname2, hstasig, mstgenero, 
        mststatus, mstcargo
        FROM msthistori a, mststudent b 
        WHERE a.hstid=b.mstid and hstyear>=%s and hstmonth>=%s and (mstgenero like %s or mstgenero like %s)
        and not (mststatus = %s or mststatus = %s) """
        valpgm = (anio, mes, sexolower, sexoupper, censurado, expulsado)
        inx=cnx.cursor(buffered=True)
        inx.execute(sqlpgm,valpgm)
        rcd_stu_name=inx.fetchall()
      else:
        name='%'+name_student+'%'
        sqlpgm = """select mstid, hstyear, hstmonth, hstname, hstid2, hstname2, hstasig, 
        mstgenero, mststatus, mstcargo
        FROM msthistori a, mststudent b 
        WHERE a.hstid=b.mstid and hstyear>=%s and hstmonth>=%s and hstname like %s and (mstgenero like %s or
        mstgenero like %s ) and not (mststatus = %s or mststatus = %s) """
        valpgm = (anio, mes, name, sexolower, sexoupper, censurado, expulsado)
        inx=cnx.cursor(buffered=True)
        inx.execute(sqlpgm,valpgm)
        rcd_stu_name=inx.fetchall()
      if not rcd_stu_name:
        flash(f'no student registration, { name_student }')
        return render_template('subtopicosfm.html', pgmid=pgmid, semanai = (rcdplan[6]), 
                               semanaf = (rcdplan[7]) , topics = (rcdplan[8]) )
      if (re.search('Video',( rcdplan[8] ))) :
            i=0
            lista=[]
            for item in rcd_stu_name:
              if not (  (re.search('ANCIANO',(item[9]))) or (re.search('SIERVO',(item[9]))) ):
                  pass
              else:
                  lista.append(item)
              i+=1
            rcd_stu_name.clear
            rcd_stu_name=lista.copy()
      #Topico_lectura_w
      return render_template('Topico_lecturafm.html', students = rcd_stu_name, pgmid=pgmid, anio = anio, mes = mes, 
                             names = name_student )
  else:    
      flash('revisar funcion de topico_lectura')
      return redirect ( url_for ( 'Index') )


@app.route('/Subtopico_revisita_aux/<idt> <idplan>', methods = ['GET','POST'])
def Subtopico_revisita_aux(idt, idplan):
    sql_mst= """ select * 
    FROM mststudent 
    WHERE mstid=%s """

    inx=cnx.cursor(buffered=True)
    inx.execute(sql_mst, (idt,))
    rcdmst = inx.fetchone()

    sql_plan = """ select * 
    FROM programamensual 
    WHERE pgmid_pm = %s """

    inx=cnx.cursor(buffered = True)
    inx.execute(sql_plan, (idplan,))
    rcdplan = inx.fetchone()

    stmt = """select hstid, hstyear, hstmonth, hstname, hstid2, hstname2, hstasig, mstgenero, mststatus 
    FROM msthistori a, mststudent b 
    WHERE a.hstid = b.mstid order by hstname2, hstyear, hstmonth """

    inx = cnx.cursor(buffered = True)
    inx.execute(stmt)
    studentshst = inx.fetchall()

    if request.method == 'GET':
      if not rcdmst :
          flash(f'error grave, no hay id titular, {idt}')
          return redirect ( url_for ('Index') )
      if not rcdplan :
          flash(f'error grave, no hay id plan maestro, {idplan}')
          return redirect ( url_for ('Index') )

      #f(Subtopico_revisita_aux)
      return render_template('Subtopico_revisita_auxfm.html', stuname = (rcdmst [1]), 
                             stugenero = (rcdmst [3]), stustatus = (rcdmst [7]), semanai = (rcdplan [6]), 
                             semanaf=(rcdplan[7]), topico=(rcdplan[8]), idpgmmonth=idplan, idt=idt) 
    else:
      periodo = request.form ['periodo_m']
      if not periodo :
          flash('must enter period, cannot be blank')
          return render_template('Subtopico_revisita_auxfm.html', stuname = (rcdmst [1]), 
                             stugenero = (rcdmst [3]), stustatus = (rcdmst [7]), semanai = (rcdplan [6]), 
                             semanaf=(rcdplan[7]), topico=(rcdplan[8]), idpgmmonth=idplan, idt=idt) 
      separarador = periodo.find('-')
      anio = int(periodo[0:separarador])
      mes = int(periodo[separarador+1:len(periodo)] )


      sql_mst = """ select MSTID, MSTNAME,MSTGENERO,MSTSTATUS  
      FROM mststudent 
      WHERE mstid = %s """

      inx=cnx.cursor(buffered = True)
      inx.execute(sql_mst,(idt,))
      rcdmst=inx.fetchone()

      sql_plan = """  select * 
      FROM programamensual 
      WHERE pgmid_pm = %s """

      inx= cnx.cursor(buffered = True)
      inx.execute(sql_plan,(idplan,))
      rcdplan = inx.fetchone()
       
      if not rcdmst :
         flash(f'error en el maestro de estudiante, {idt}')
         return render_template('Subtopico_revisita_auxfm.html', stuname = (rcdmst [1]), 
                             stugenero = (rcdmst [3]), stustatus = (rcdmst [7]), semanai = (rcdplan [6]), 
                             semanaf=(rcdplan[7]), topico=(rcdplan[8]), idpgmmonth=idplan, idt=idt) 

      if not rcdplan :
         flash('error en el plan maestro, {idplan}')
         return render_template('Subtopico_revisita_auxfm.html', stuname = (rcdmst [1]), 
                             stugenero = (rcdmst [2]), stustatus = (rcdmst [3]), semanai = (rcdplan [6]), 
                             semanaf=(rcdplan[7]), topico=(rcdplan[8]), idpgmmonth=idplan, idt=idt) 
      try:
       inx=cnx.cursor(buffered=True)
       sqlcrta = """ drop table if exists hsta """
       inx.execute(sqlcrta)
       cnx.commit
       inx=cnx.cursor(buffered=True)
       sqlcrta=""" create table hsta as select a.mstid, c.hstyear, c.hstmonth, a.mstname, a.mstgenero, a.mststatus,
                           c.hstasig, c.hstid2, hstname2 
                           FROM msthistori c 
                           INNER JOIN mststudent a 
                           ON c.hstid = a.mstid """
       inx.execute(sqlcrta)
       cnx.commit
      except:
       inx=cnx.cursor(buffered=True)
       sqlcrta=""" create table hsta as select a.mstid, c.hstyear, c.hstmonth, a.mstname, a.mstgenero, a.mststatus,
                           c.hstasig, c.hstid2, hstname2 
                           FROM msthistori c 
                           INNER JOIN mststudent a 
                           ON c.hstid = a.mstid """
       inx.execute(sqlcrta)
       cnx.commit

      try:
          inx=cnx.cursor(buffered=True)
          sqlcrtb = """ drop table if exists hstb """
          inx.execute(sqlcrtb)
          cnx.commit
          inx=cnx.cursor(buffered=True)
          sqlcrtb = """ create table hstb as select a.mstid, a.hstyear, a.hstmonth, a.mstname, a.mstgenero, a.mststatus, a.hstasig 
          FROM hsta a  
          INNER JOIN mststudent b
          ON a.hstid2 = b.mstid """
          inx.execute(sqlcrtb)
          cnx.commit
      except:
          inx=cnx.cursor(buffered=True)
          sqlcrtb = """ create table hstb as select a.mstid, a.hstyear, a.hstmonth, a.mstname, a.mstgenero, a.mststatus, a.hstasig 
          FROM hsta a  
          INNER JOIN mststudent b
          ON a.hstid2 = b.mstid """
          inx.execute(sqlcrtb)
          cnx.commit

      name = request.form ['name']


      if not name :
          sqlhst = """ select distinct a.mstid, a.hstyear, a.hstmonth, a.mstname, a.mstgenero, a.mststatus,
          c.idmst, c.namemst, c.generomst, c.statusmst,
          a.hstasig FROM hsta a 
          INNER JOIN hstb c 
          ON a.hstid2 = c.idmst
          WHERE a.hstyear>=%s and a.hstmonth>=%s
          ORDER BY a.mstname, a.hstyear, a.hstmonth """
          hstval = (anio, mes)
          inx.execute(sqlhst,hstval)
          studentshst=inx.fetchall()
          if not studentshst :
            flash(f'error, review historical information of students')
            return render_template('Subtopico_revisita_auxfm.html', stuname = (rcdmst [1]), 
                             stugenero = (rcdmst [2]), stustatus = (rcdmst [3]), semanai = (rcdplan [6]), 
                             semanaf=(rcdplan[7]), topico=(rcdplan[8]), idpgmmonth=idplan, idt=idt) 

      else:
          names = '%'+name+'%'
          #  SELECT `mstid`, `hstyear`, `hstmonth`, `mstname`, `mstgenero`, `mststatus`, `hstasig`, `hstid2`, `hstname2` FROM `hsta` WHERE 1

          # SELECT `mstid`, `hstyear`, `hstmonth`, `mstname`, `mstgenero`, `mststatus`, `hstasig` FROM `hstb` WHERE 1

          sqlhst = """ select distinct a.mstid, a.hstyear, a.hstmonth, a.mstname, a.mstgenero, a.mststatus,
          b.mstid, b.mstname, b.mstgenero, b.mststatus, a.hstasig 
          FROM hsta a 
          INNER JOIN hstb b 
          ON a.hstid2 = b.mstid
          WHERE a.hstyear>=%s and a.hstmonth>=%s and (a.mstname like %s or  b.mstname like %s) 
          ORDER BY a.hstyear, a.hstmonth, a.mstname, b.mstname """
          hstval = (anio, mes, names, names)
          inx.execute(sqlhst,hstval)
          studentshst=inx.fetchall()
          if not studentshst :
            flash(f'error3, review historical information of, {name}')
            return render_template('Subtopico_revisita_auxfm.html', stuname = (rcdmst [1]), 
                             stugenero = (rcdmst [2]), stustatus = (rcdmst [3]), semanai = (rcdplan [6]), 
                             semanaf=(rcdplan[7]), topico=(rcdplan[8]), idpgmmonth=idplan, idt=idt) 

      return render_template('subtopico_rev_aux_filrofm.html', 
                                students=studentshst,
                                stuname=(rcdmst[1]),
                                stugenero=(rcdmst[2]), 
                                stustatus=(rcdmst[3]), 
                                semanai=(rcdplan[6]), 
                                semanaf=(rcdplan[7]), 
                                topics=(rcdplan[8]), idt=idt, idplan=idplan)

@app.route('/Subtopico_rev_pre_wrt/<idaux> <idplan> <idt>', methods=['POST','GET'])
def Subtopico_rev_pre_wrt (idaux, idplan, idt):
  print(request.method)
  if request.method=='GET':
      inx = cnx.cursor(buffered=True)
      stmt = """ SELECT mstid, mstname, mstgenero, msttipoe, mststatus FROM mststudent WHERE mstid = %s """
      inx.execute(stmt,(idt,) )
      rcdmst = inx.fetchone()

      inx = cnx.cursor(buffered=True)
      stmt = """ SELECT mstid, mstname, mstgenero, msttipoe, mststatus FROM mststudent where mstid = %s """
      inx.execute(stmt,(idaux,) )
      rcdmsta = inx.fetchone()

      inx = cnx.cursor(buffered=True)
      stmt = """ SELECT * FROM programamensual where pgmid_pm = %s """
      inx.execute(stmt,(idplan,) )
      rcdplan = inx.fetchone()

      if not rcdmst :
          flash(f'error grave: no hay Id titular:, {idt}')
          return redirect( url_for ('auxiliar', idt=idt,idpgmmonth=idplan))

      if not rcdplan :
          flash(f'error grave: no hay id plan: {idplan} ')
          return redirect( url_for ('auxiliar', idt=idt,idpgmmonth=idplan))

      if not rcdmsta :
          flash(f'error grave: no hay Id auxiliar, {idaux}')
          return redirect( url_for ('auxiliar', idt=idt,idpgmmonth=idplan))

      if ( rcdmst[2] ) != ( rcdmsta[2] ):
          flash(f'error en datos, revise el genero, {( rcdmsta[1] )} ')
          return render_template('Subtopico_revisita_auxfm.html', stuname = (rcdmst [1]),
          stugenero = (rcdmst [2]), stustatus = (rcdmst [4]), semanai = (rcdplan [6]), 
          semanaf=(rcdplan[7]), topico=(rcdplan[8]), idpgmmonth=idplan, idt=idt) 

      return render_template('Subtopico_wrt_revisita.html', dataprim=rcdplan, recstudt = rcdmst, 
                             recstuda = rcdmsta)
  else:
      return render_template('revisita.html')


@app.route('/Topico_lectura_w/<idt> <idpgm_month>')
def pre_grabacion_lect(idt, idpgm_month):
  inx = cnx.cursor(buffered=True)
  stmt = """ select mstid, mstname, mstgenero, msttipoe, mststatus 
  FROM mststudent where mstid = %s """
  inx.execute(stmt,(idt,) )
  rcdmst = inx.fetchone()

  if not rcdmst:
      flash(f'maestro de estudiante no hay, {idt}')
      return redirect(url_for('Index'))

  stmt=""" select * from programamensual where pgmid_pm = %s """
  inx.execute(stmt,(idpgm_month,))
  rcdplan = inx.fetchone()

  if not rcdplan:
    flash(f'registro para el programa mensual no hay, {idpgm_month}')
    return redirect (url_for('Index'))

  return render_template('Topico_pre_w_lecturafm.html', dataprim=rcdplan, rcdstudent = rcdmst)







@app.route('/srv_hst_mst_namexyz/<mstida> <pgmid_id>')
def auxiliar(mstida, pgmid_id):
  inx = cnx.cursor(buffered = True  )
  stmt = """select * FROM programamensual where pgmid_pm = %s """
  inx.execute(stmt, (pgmid_id,))
  rcdplan = inx.fetchone()

  inx = cnx.cursor(buffered = True  )
  stmt = """select hstid, hstyear, hstmonth, hstname, hstid2,  hstname2, hstasig, mstgenero, mststatus 
  FROM msthistori a INNER JOIN mststudent b ON a.hstid2 = b.mstid
  WHERE a.hstid2 = %s
  ORDER by hstname2, hstyear, hstmonth """
  inx.execute(stmt,( mstida ,))
  studentshst = inx.fetchone()

  if not studentshst:
      flash('el id auxiliar no existe, {mstida}')
      return render_template('topico_revisitafm.html', students = studentshst, pgmid=pgmid_id,
                        semanai = (rcdplan[6]), semanaf = (rcdplan[7]) , tipo= (rcdplan[8]) )

  return render_template('Subtopico_revisita_auxfm.html', stuname = (studentshst [5]), 
                             stugenero = (studentshst [7]), stustatus = (studentshst [8]), semanai = (rcdplan [6]), 
                             semanaf=(rcdplan[7]), topico=(rcdplan[8]), idpgmmonth=pgmid_id, idt=mstida) 


@app.route('/Topico_lect_upd_vmc/<pgmid> <idt>', methods=['GET', 'POST'])
def Topico_lect_upd_vmc(pgmid, idt):
  if request.method == 'POST':
    inx = cnx.cursor(buffered=True)
    stmtsql = """ select * from programamensual where pgmid_pm = %s """
    inx.execute(stmtsql, (pgmid,) )
    rcdpgm_month = inx.fetchone()
      
    meses = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    bool=False
    mesnum=1

    for mes in meses:
      mes_buscado = (rcdpgm_month[5]).find(mes)

      if int(mes_buscado) >= 0 :
        index_guion=(rcdpgm_month[5]).find('-')
        index_blank = (rcdpgm_month[5]).find(" ")
        bool=True
        flagmesinicial = False
        
        i=0
        while i < len(meses):
          if ((rcdpgm_month[5])[0:index_blank]) == meses[i]:
             flagmesinicial=True
             if i == len(meses):
                 j=i 
             else:
                 j=i+1
             break
          i+=1

        primerafecha = (rcdpgm_month[5])[0:index_guion-1]

        if i<9 and flagmesinicial == True:
           primerafecha = primerafecha.replace(meses[i], ('0'+str(j)))
        else:
           primerafecha = primerafecha.replace(mes, str(mesnum))

        if (flagmesinicial  == True):
          #el texto empieza con el nombre del mes
          primerafechames = primerafecha[0:2]
          primerafechadia = primerafecha[3:5]
          primerafechaano = primerafecha[6:11]  
          fechafalse = datetime(int( primerafechaano ), int( primerafechames ),  int( primerafechadia ))
          pgmdateinicial = fechafalse.strftime('%d-%m-%Y')
        else:
          primerafecha = primerafecha + ' a las 00:00'
          pgmdateinicial = datetime.strptime(primerafecha, '%d de %m de %Y a las %H:%M')
          pgmdateinicial = pgmdateinicial.strftime('%d-%m-%Y')
      mesnum+=1  

    if not bool:
        sqlstmt=""" select * from mststudent where mstid=%s"""
        inx=cnx.cursor(buffered=True)
        inx.execute(sqlstmt,(idt,))
        rcd_stu_name = inx.fetchone()
        flash (f'fecha full no tiene mes latino:, (rcdpgm_month[5])')
        return redirect(url_for('Index'))


    fechafalse = datetime(int(pgmdateinicial[6:10]), int(pgmdateinicial[3:5]),  int(pgmdateinicial[0:2]))
    pgmdatefinal = fechafalse + timedelta(days=6)
    pgmdatefinal = pgmdatefinal.strftime('%d-%m-%Y')
    fecha = datetime.now().date()
    fecha = date.today()
    hora = datetime.now().time()
    pgmdateinicial = datetime.strptime(str(pgmdateinicial), '%d-%m-%Y')
    pgmdatefinal = datetime.strptime(str(pgmdatefinal), '%d-%m-%Y')
    pgmdateinicial = datetime.date(pgmdateinicial)
    pgmdatefinal = datetime.date(pgmdatefinal)
    asgsemanaidte = pgmdateinicial
    asgsemanafdte = pgmdatefinal

        # print(dir(datetime))

    inx = cnx.cursor(buffered=True)
    updatesql = """ UPDATE programamensual SET actualizadofecha = '{}', actualizadohora = '{}',
        pgmdateinicial = '{}', pgmdatefinal = '{}'
    WHERE
        pgmid_pm = '{}'
    """.format(fecha, hora, pgmdateinicial, pgmdatefinal, pgmid)

    
    pgmfechaistr = pgmdateinicial.strftime('%B %d, %Y')
    pgmfechafstr = pgmdatefinal.strftime('%B %d, %Y')

    # peticion
    pgmtipoasig =  request.form['pgmtipoasig']
    pgmtexto = request.form['pgmtexto']
    pgmsala = request.form['Req_sala']
    pgmtipot = request.form['Req_tipot']
    pgmnombret = request.form['Req_nombret']
    pgmgenerot = request.form['Req_sexot']

    inx = cnx.cursor(buffered=True)
    sqlinsert = """INSERT INTO asignaciones (idt_asig, pgmano, pgmmes, pgmtiempo, pgmleccion, 
    pgmsemanafull, pgmtipoasig, pgmtexto, pgmsala, pgmtipot, pgmtipoa, pgmnombret, pgmnombrea, 
    pgmgenerot, pgmgeneroa, cumplio, pgmdateinicial, pgmdatefinal, pgmfechaistr, pgmfechafstr) 
    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    sqlvalue = (idt, (rcdpgm_month[1]), (rcdpgm_month[2]), (rcdpgm_month[3]), (rcdpgm_month[4]), 
    (rcdpgm_month[5]), pgmtipoasig, pgmtexto, pgmsala, pgmtipot, ' ', pgmnombret, ' ', pgmgenerot, 
    ' ', 'XY', pgmdateinicial, pgmdatefinal, pgmfechaistr, pgmfechafstr)

    sql_mst = """ select * from mststudent where mstid = %s """
    cnxsql = cnx.cursor(buffered=True)
    cnxsql.execute(sql_mst, (idt,))
    rcd_mst = cnxsql.fetchone()

    sql_hst = """ insert into msthistori 
    values ( %s, %s, %s, %s, %s, %s, %s) """
    sql_hst_values = (idt, (rcdpgm_month[1]), (rcdpgm_month[2]), (rcd_mst[1]), idt, (rcd_mst[1]), pgmtipoasig )

    sqlkeydup = """ select * from msthistori 
    where hstyear = %s and hstmonth = %s and hstname = %s  """
    sqlkeydupv = ((rcdpgm_month[1]), (rcdpgm_month[2]), (rcd_mst[1]) )
    inx=cnx.cursor(buffered=True)
    inx.execute(sqlkeydup, sqlkeydupv)
    rcddup=inx.fetchall()
    if rcddup != None:
        for keydup in rcddup:
            print((keydup[1]), (keydup[2]), (keydup[3]) )
            print( 'anioo',' ',(rcdpgm_month[1]), ' ','mes',' ', (rcdpgm_month[2]),' ','nombre',' ',(rcd_mst[1])  )
            if  ( (keydup[1]) ==  (rcdpgm_month[1]) and
                  (keydup[2]) ==  (rcdpgm_month[2]) and
                  (keydup[3]) ==  (rcd_mst[1]) ) :
                flash(f'Error-1. student already assigned in that period, {(rcd_mst[1])} ' )
                return redirect ( url_for ('Index') )
    print('NO hay duplicado en el historico: ', datetime.now (), ' ', sqlkeydupv)

    try:        
      cnxsql = cnx.cursor(buffered=True)
      inx.execute(updatesql)
      flash(f'base programa mensual actualizado correctamente, {pgmid}')
    except errorcode as e:
      print(e)
      flash(f'no se pudo actualizar base programa mensual, {pgmid}')
      return redirect(url_for('Index'))

    try:
      cnxsql = cnx.cursor(buffered=True)
      inx.execute(sqlinsert,sqlvalue)
      flash(f'Asignacion del estudiante creada exitosamente, {pgmnombret}')
    except Exception as e:
      print(e)
      flash('Error al crear asignacion del estudiante, revise por favor')
      return redirect(url_for('Index'))

    try:
        cnxsql = cnx.cursor(buffered=True)
        cnxsql.execute(sql_hst, sql_hst_values)
        flash('se creo la asignacion del estudiante en base historica')
    except Exception as e:
        print(e)
        flash('error al insertar record historico')
  return redirect(url_for('Index'))



@app.route('/srv_aux/<idname> <idpgmmonth> <idt>')
def procesoest_aux (idname, idpgmmonth, idt ):
  print(idname,' ' , idpgmmonth, ' ', idt)
  inx = cnx.cursor(buffered=True)
  stmt = """ SELECT mstid, mstname, mstgenero, msttipoe, mststatus FROM mststudent where mstid = %s """
  inx.execute(stmt,(idt,) )
  recstudt = inx.fetchone()
  pgmgenerot=(recstudt[2])
  if recstudt == None:
      return redirect(url_for('Index'))
  stmt = """ SELECT mstid, mstname, mstgenero, msttipoe, mststatus FROM mststudent where mstname = %s """
  inx.execute(stmt,(idname,) )
  recstuda = inx.fetchone()
  pgmgeneroa=(recstuda[2])
  if recstuda == None :
       return redirect(url_for('Index'))
  if pgmgenerot != pgmgeneroa:
    flash(f'students must be of the same sex, {idname}')
    inx = cnx.cursor()
    stmt = 'SELECT hstid, hstyear, hstmonth, hstname, hstid2, hstname2, hstasig, mstgenero, mststatus FROM msthistori a, mststudent b where a.hstid = b.mstid order by hstname2, hstyear, hstmonth '
    inx.execute(stmt)
    studentshst = inx.fetchall()
    return render_template('inqhistoricoa.html', students = studentshst, idpgmmonth=idpgmmonth, idt=idt)
  stmt=""" select * from programamensual where pgmid_pm = %s """
  inx.execute(stmt,(idpgmmonth,))
  dataprim = inx.fetchone()
  if dataprim == None :
    return redirect (url_for('Index'))
  tipoasignacion = ( dataprim[8] )
  print(tipoasignacion)
  return render_template('Subtopico_wrt_revisita.html', dataprim=dataprim, recstudt = recstudt, recstuda = recstuda)

     
@app.route('/Subtopico_rev_upd/<int:pgmid> <idt> <ida>', methods=['POST','GET'])
def grabaasignacion(pgmid, idt, ida):
  if request.method == 'POST':
      pgmtipoasig =  request.form['pgmtipoasig']
      pgmtexto = request.form['pgmtexto']
      pgmsala = request.form['Req_sala']
      pgmtipot = request.form['Req_tipot']
      pgmtipoa = request.form['Req_tipoa']
      pgmnombret = request.form['Req_nombret']
      pgmnombrea = request.form['Req_nombrea']
      pgmgenerot = request.form['Req_sexot']
      pgmgeneroa = request.form['Req_sexoa']
      inx = cnx.cursor(buffered=True)
      stmtsql = """ select * from programamensual where pgmid_pm = %s """
      inx.execute(stmtsql, (pgmid,) )
      rcdpgm_month = inx.fetchone()

      inx = cnx.cursor(buffered=True)
      stmtsql = """ select * from mststudent where mstid = %s """
      inx.execute(stmtsql, (idt,) )
      rcdstudt = inx.fetchone()

      inx = cnx.cursor(buffered=True)
      stmtsql = """ select * from mststudent where mstid = %s """
      inx.execute(stmtsql, (ida,) )
      rcdstuda = inx.fetchone()
      meses = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
      bool=False
      mesnum=1 
      for mes in meses:
        indicadorencontrado = (rcdpgm_month[5]).find(mes)
        if int(indicadorencontrado) >= 0 :
            indicedeguion=(rcdpgm_month[5]).find('-')
            indexblanco = (rcdpgm_month[5]).find(" ")
            bool=True
            flagmesinicial = False
            i=0
            while i < len(meses):
                if ((rcdpgm_month[5])[0:indexblanco]) == meses[i]:
                    flagmesinicial=True
                    if i == len(meses):
                        j=i 
                    else:
                        j=i+1
                        break
                i+=1
            primerafecha = (rcdpgm_month[5])[0:indicedeguion-1]
            if i<9 and flagmesinicial == True:
                primerafecha = primerafecha.replace(meses[i], ('0'+str(j)))
            else:
                primerafecha = primerafecha.replace(mes, str(mesnum))

            if (flagmesinicial  == True):
                #el texto empieza con el nombre del mes
                primerafechames = primerafecha[0:2]
                primerafechadia = primerafecha[3:5]
                primerafechaano = primerafecha[6:11]  
                fechafalse = datetime(int( primerafechaano ), int( primerafechames ),  int( primerafechadia ))
                pgmdateinicial = fechafalse.strftime('%d-%m-%Y')
            else:
                primerafecha = primerafecha + ' a las 00:00'
                pgmdateinicial = datetime.strptime(primerafecha, '%d de %m de %Y a las %H:%M')
                pgmdateinicial = pgmdateinicial.strftime('%d-%m-%Y')
            mesnum+=1

      if not bool:
         return redirect(url_for('Index'))

      fechafalse = datetime(int(pgmdateinicial[6:10]), int(pgmdateinicial[3:5]),  int(pgmdateinicial[0:2]))
      pgmdatefinal = fechafalse + timedelta(days=6)
      pgmdatefinal = pgmdatefinal.strftime('%d-%m-%Y')
      fecha = datetime.now().date()
      fecha = date.today()
      hora = datetime.now().time()
      pgmdateinicial = datetime.strptime(str(pgmdateinicial), '%d-%m-%Y')
      pgmdatefinal = datetime.strptime(str(pgmdatefinal), '%d-%m-%Y')
      pgmdateinicial = datetime.date(pgmdateinicial)
      pgmdatefinal = datetime.date(pgmdatefinal)

        # print(dir(datetime))

      inx = cnx.cursor(buffered=True)
      stmtsql = """ select * from programamensual where pgmid_pm = %s """
      inx.execute(stmtsql, (pgmid,) )
      rcdpgm_month = inx.fetchone()

      updatesql = """ 
      UPDATE programamensual
      SET actualizadofecha = '{}', 
            actualizadohora = '{}',
            pgmdateinicial = '{}',
            pgmdatefinal = '{}'
      WHERE
            pgmid_pm = '{}' 
            """.format(fecha, hora, pgmdateinicial, pgmdatefinal, pgmid)


      pgmfechaistr = pgmdateinicial.strftime('%B %d, %Y')
      pgmfechafstr = pgmdatefinal.strftime('%B %d, %Y')


      sqlinsert = """INSERT INTO asignaciones (idt_asig, ida_asig, pgmano, pgmmes, pgmtiempo, pgmleccion, 
      pgmsemanafull, pgmtipoasig, pgmtexto, pgmsala, pgmtipot, pgmtipoa, pgmnombret, pgmnombrea, pgmgenerot, 
      pgmgeneroa, cumplio, pgmdateinicial, pgmdatefinal, pgmfechaistr, pgmfechafstr) 
      VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
      sqlvalue = (idt, ida, (rcdpgm_month[1]), (rcdpgm_month[2]), (rcdpgm_month[3]), (rcdpgm_month[4]), 
      (rcdpgm_month[5]), pgmtipoasig, pgmtexto, pgmsala, pgmtipot, pgmtipoa, pgmnombret, pgmnombrea, 
      pgmgenerot, pgmgeneroa, 'XY', pgmdateinicial, pgmdatefinal, pgmfechaistr, pgmfechafstr)

      sql_hst = """ insert into msthistori values ( %s, %s, %s, %s, %s, %s, %s) """
      sql_hst_values=(idt,(rcdpgm_month[1]),(rcdpgm_month[2]),(rcdstudt[1]),ida,(rcdstuda[1]),pgmtipoasig)
      


      sqlkeydup = """ select * from msthistori 
      where hstyear = %s and hstmonth = %s and hstname = %s  """
      sqlkeydupv = ((rcdpgm_month[1]), (rcdpgm_month[2]), (rcdstudt[1]) )
      inx=cnx.cursor(buffered=True)
      inx.execute(sqlkeydup, sqlkeydupv)
      rcddup=inx.fetchall()
      if rcddup != None:
        for keydup in rcddup:
            print((keydup[1]), (keydup[2]), (keydup[3]) )
            print('test duplicado revisita ' 'anioo',' ',(rcdpgm_month[1]), ' ','mes',' ', (rcdpgm_month[2]),' ','nombre',' ',(rcdstudt[1])  )
            if  ( (keydup[1]) ==  (rcdpgm_month[1]) and
                  (keydup[2]) ==  (rcdpgm_month[2]) and
                ( (keydup[3]) ==  (rcdstudt[1]) or  (keydup[3]) ==  (rcdstuda[1]) )   ) :
                flash(f'Error-2. student already assigned in that period, {(rcdstudt[1])} ' )
                return redirect ( url_for ('Index') )
      print('NO hay duplicado en el historico: ', datetime.now (), ' ', sqlkeydupv)


      try:
          cnxsql = cnx.cursor(buffered=True)
          cnxsql.execute(sql_hst, sql_hst_values)
          cnx.commit()
          flash('Se registro la asignacion de los estudiantes en el historico')
      except mysql.connector.errors.IntegrityError as e:
          print(e)
          flash(f'error1.1 al intentar grabar asignacion en base historico, {pgmnombret}')
          return redirect(url_for('Index'))


      try:
          inx = cnx.cursor(buffered=True)
          inx.execute(updatesql)
          flash(f'se actualizo la base: plan maestro, {pgmid}')
      except errorcode as e:
          print(e)
          flash(f'error.1.2 no se pudo actualizar base plan maestro, {pgmid}')
          return redirect(url_for('Index'))

      try:
          inx = cnx.cursor(buffered=True)
          inx.execute(sqlinsert,sqlvalue)
          flash(f'Se creo la asignacion al estudiante, {pgmnombret}')
          return redirect(url_for('Index'))
      except Exception as e:
          print ("This is an error message!{}".format(e))
          flash(f'error1.3 Hubo error al intentar grabar base asignaciones, {pgmnombret}')
          return redirect(url_for('Index'))

  return redirect(url_for('Index'))

@app.route('/Subtopico_rev_pre_wrtxyz/<ida> <idpgmmonth> <idt>', methods =['POST','GET'])
def Subtopico_rev_pre_wrtxyz (ida, idpgmmonth, idt ):
  if request.method=='GET':
      inx = cnx.cursor(buffered=True)
      stmt = """ SELECT mstid, mstname, mstgenero, msttipoe, mststatus FROM mststudent where mstid = %s """
      inx.execute(stmt,(idt,) )
      rcdmstt = inx.fetchone()

      inx = cnx.cursor(buffered=True)
      stmt=""" select * from programamensual where pgmid_pm = %s """
      inx.execute(stmt,(idpgmmonth,))
      rcdplan = inx.fetchone()

      inx = cnx.cursor(buffered=True)
      stmt = """ SELECT mstid, mstname, mstgenero, msttipoe, mststatus FROM mststudent where mstid = %s """
      inx.execute(stmt,(ida,) )
      rcdmsta = inx.fetchone()

      inx = cnx.cursor(buffered=True)
      stmt = """select hstid, hstyear, hstmonth, hstname, hstid2, hstname2, hstasig, mstgenero, mststatus 
      FROM msthistori a, mststudent b where a.hstid = b.mstid order by hstname2, hstyear, hstmonth """
      inx.execute(stmt)
      rcdhst = inx.fetchall()

      if not rcdmstt:
          flash(f'Id del estudiante principal no existe en mststudent, {idt}')
          return redirect(url_for('Index'))

      if not rcdplan:
          flash(f'Id del plan maestro no existe en programa mensual, {idpgmmonth}')
          return redirect (url_for('Index'))

      if not rcdhst:
          flash(f'estudiantes historicos no existe en msthistori, {idt}')
          return redirect(url_for('Index'))

      if not rcdmsta:
          flash(f'Id del estudiante auxiliar no existe en mststudent, {ida}')
          return render_template('subtopico_rev_aux_filrofm.html', 
                                students=rcdhst,
                                stuname=(rcdmstt[1]),
                                stugenero=(rcdmstt[3]), 
                                stustatus=(rcdmstt[4]), 
                                semanai=(rcdplan[6]), 
                                semanaf=(rcdplan[7]), 
                                topico=(rcdplan[8]), idt=idt, idplan=idpgmmonth)
            
      pgmgenerot=(rcdmstt[2])
      pgmgeneroa=(rcdmsta[2])
      if pgmgenerot != pgmgeneroa:
        flash(f'students must be of the same sex, {pgmgeneroa}')
        return render_template('Subtopico_revisita_auxfm.html', 
                                stuname  =(rcdmstt[1]),
                                stugenero=(rcdmstt[3]), 
                                stustatus=(rcdmstt[4]), 
                                semanai  =(rcdplan[6]), 
                                semanaf  =(rcdplan[7]), 
                                topico   =(rcdplan[8]),
                                idpgmmonth=idpgmmonth, idt=idt)

      return render_template('Subtopico_wrt_revisita.html', dataprim=rcdplan, recstudt = rcdmstt, 
                             recstuda = rcdmsta)
  else:
      pass

@app.route('/registrazione', methods=['POST'])
def registration():
  if request.method == 'POST':
    Req_semana_inicial = request.form['Req_semana_inicial']
    if (Req_semana_inicial == ''):
        flash('missing to enter period week and year')
        return redirect( url_for ( 'ipvmd' ) )

    #manejo de semanas
    anosemana = int(Req_semana_inicial[0:4])
    semana = int(Req_semana_inicial[6:8])
    Req_fecha_inicial = date(anosemana,1,1)+relativedelta(weeks=semana-1, weekday=MO(1))
    #fin manejo semanas

    yystr = Req_fecha_inicial.strftime('%Y')
    mm = Req_fecha_inicial.strftime('%m')
    dd = Req_fecha_inicial.strftime('%d')
    yydec = int(yystr)
    mmdec = int(mm)
    dddec = int(dd)

    fechaint = int(str(yystr+mm+dd))
    fechaparcial = datetime.strptime(str(fechaint), '%Y%m%d')
    # 2020-09-28 00:00:00   <class 'datetime.datetime'>
    pgmfechaistr = fechaparcial.strftime('%B %d, %Y')
    # fecha final September 28, 2020
    # calculo de la fecha final de la semana
    fechaparcial = datetime(year=yydec, month=mmdec, day=dddec)

    fecha_final = fechaparcial + timedelta(days=6)
    fechasemanafinal = fecha_final.date()

    pgmfechafstr = fecha_final.strftime('%B %d, %Y')

    Req_texto = request.form['Req_texto']
    if not Req_texto:
        flash('missing to enter the description of the topic')
        return redirect ( url_for ('ipvmd') )


    pretiempo=re.findall ('\d+.mins.',Req_texto)    
    if not pretiempo:
        flash(f'no hay un formato correcto del tiempo. revise formato de minutos')
        return render_template('plan_maestro.html')
    pretiempo=str(pretiempo)
    pretime=re.findall('\d+',pretiempo)
    inxtiempo=len( pretime )
    Req_tiempo=pretime[ inxtiempo - 1 ]
    print( Req_tiempo,' ',type ( Req_tiempo  ))
    postiempo = Req_texto.find( Req_tiempo  )
    Req_tipo=Req_texto[ 0 :postiempo - 1 ]    
    print( Req_tipo )

    inxtipo=Req_tipo.find('Video')
    print( inxtipo )
    if inxtipo == -1:
        preleccion=re.findall('\w\w\w\.\s\d+',Req_texto)
        if not preleccion:
            flash(f'no hay un formato correcto de la leccion. revise formato de leccion')
            return render_template('plan_maestro.html')
        preleccion=str( preleccion )
        pretime=re.findall('\d+',preleccion)
        inxtiempo=len( pretime )
        Req_leccion=pretime[ inxtiempo - 1 ]
        print( Req_leccion  ) 
    else:
        Req_leccion = 99
    fechaconcatenada = pgmfechaistr + ' ' + '-' + ' ' + pgmfechafstr + ' ' + '-' + ' ' + Req_tipo

    fechahoracurrent = datetime.now()
    anocurrent = fechahoracurrent.year
    mescurrent = fechahoracurrent.month
    diacurrent = fechahoracurrent.day
    fechacurrent = fechahoracurrent.date()
    horacurrent = fechahoracurrent.strftime('%X')
    horaupdate =  timedelta(hours=23, minutes=59, seconds=59)
    fechaupdate = date.fromisoformat('2000-12-31')
    fechaupdate = date(2000, 12, 31)

    semanacorriente = int(date(yydec, mmdec, dddec).strftime("%V")) 
    numerodiasemana = date(yydec, mmdec, dddec).weekday()
    arraydiasemana=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    nombredeldiadelasemana = date(yydec, mmdec, dddec).strftime("%A")

    # clave duplicada programa mensual
    inx = cnx.cursor(buffered=True)
    stmtsqltest = 'select * from programamensual where pgmano=%s and pgmmes=%s and pgmtiempo=%s and pgmleccion=%s and pgmsemanafull=%s'
    stmtsqlvalue=(yydec, mmdec, Req_tiempo, Req_leccion,  fechaconcatenada)
    inx.execute(stmtsqltest, stmtsqlvalue)

    dbpgmmensual = inx.fetchone()

    if dbpgmmensual != None:
        flash('error: Datos fueron previamente ingresados en el PROGRAMA MENSUAL')
        return render_template('plan_maestro.html')

    stmtsql = ('select * from controlweek where yearcurrent = %s and weekcurrent = %s order by kountcurrent desc')
    stmtvalue = (yydec, semanacorriente)
    inx = cnx.cursor(buffered=True)
    inx.execute(stmtsql,stmtvalue)
    datadb = inx.fetchone()

    if datadb == None:
        if (nombredeldiadelasemana == arraydiasemana[numerodiasemana]):
            kontador=1
            inx = cnx.cursor(buffered=True)
            stmtsql =  """INSERT INTO programamensual (pgmano, pgmmes, pgmtiempo, pgmleccion, pgmsemanafull, pgmtipoasig, pgmtexto, pgmdateinicial, pgmdatefinal, pgmsemanai, pgmsemanaf,pgmmesletra,ingresousuario, ingresofecha, ingresohora, ingresopgm, actualizadouser,  actualizapgm, numerosemana) 
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            stmtvalue =  (yydec, mmdec, Req_tiempo, Req_leccion,  fechaconcatenada, Req_tipo, Req_texto, Req_fecha_inicial, fechasemanafinal, pgmfechaistr, pgmfechafstr,'xxxxxxxxxx', 'isidro', fechacurrent, horacurrent, 'appx.py', ' ',  ' ', semanacorriente)
            try:
                inx.execute(stmtsql, stmtvalue)
                flash('asignacion mensual DATA INGRESADA EN LA BASE ')
                try:
                    stmtsqlweek='insert into controlweek (yearcurrent, weekcurrent, kountcurrent) values(%s, %s, %s)'
                    stmtvalueweek=(yydec, semanacorriente, kontador)
                    inx=cnx.cursor(buffered=True)
                    inx.execute(stmtsqlweek,stmtvalueweek)
                    cnx.commit()
                    flash(' control de semanas APERTURA DE SEMANA ')
                    return render_template('plan_maestro.html')
                except errorcode as e:
                    print(e)
                    flash('CONTROL DE SEMANA - error al ingresar datos')
                    return render_template('plan_maestro.html')
            except errorcode as e:
                print(e)
                flash('asignacion mensual - Error al ingresar datos ')
                return render_template('plan_maestro.html')
        else:        
            flash('Error en el ingreso del Inicio de la Semana')
            return render_template('plan_maestro.html')

    elif  (datadb[2]) <= 4:
      if (nombredeldiadelasemana == arraydiasemana[numerodiasemana]):
          kontador = (datadb[2]) + 1
          stmtsql =  'INSERT INTO programamensual (pgmano, pgmmes, pgmtiempo, pgmleccion, pgmsemanafull, pgmtipoasig, pgmtexto, pgmdateinicial, pgmdatefinal, pgmsemanai, pgmsemanaf,pgmmesletra,ingresousuario, ingresofecha, ingresohora, ingresopgm, actualizadouser,  actualizapgm, numerosemana) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
          stmtvalue =  (yydec, mmdec, Req_tiempo, Req_leccion,  fechaconcatenada, Req_tipo, Req_texto, Req_fecha_inicial, fechasemanafinal, pgmfechaistr, pgmfechafstr,'xxxxxxxxxx', 'isidro', fechacurrent, horacurrent, 'appx.py', ' ', ' ', semanacorriente)
          try:
              inx.execute(stmtsql, stmtvalue)
              flash('DATA INGRESADA EN LA BASE programa de asignacion mensual')
              try:
                stmtsql='insert into controlweek (yearcurrent, weekcurrent, kountcurrent) values(%s, %s, %s)'
                stmtvalue=(yydec, semanacorriente, kontador)
                inx=cnx.cursor(buffered=True)
                inx.execute(stmtsql,stmtvalue)
                cnx.commit()
                flash('DATA INGRESADA EN LA BASE "control de semanas"')
                return render_template('plan_maestro.html')
              except errorcode as e:
                print(e)
                flash('error al ingresar datos en la base control de semanas controlweek')
                return render_template('plan_maestro.html')
          except errorcode as e:
              print(e)
              flash('error al ingresar datos en la base "programa de asignacion mensual"')
              return render_template('plan_maestro.html')
      else:
        flash('Error en el ingreso de Inicio de Semana')
        return render_template('plan_maestro.html')
    else:
      flash('Error en el numero de asignaciones, excede a 5')
      return render_template('plan_maestro.html')

@app.route('/plan_maestro')
def ipvmd():

  anocurrent = date.today() 
  anocurrent = int(anocurrent.year)

  return render_template('plan_maestro.html')

@app.route('/subtopicos/<pgmid_pm>', methods=['POST', 'GET'])
def subtopicos(pgmid_pm):
  if  request.method=='GET':
      sql_pgm = """select * from programamensual where pgmid_pm = %s """
      inx=cnx.cursor()
      inx.execute(sql_pgm,(pgmid_pm,))
      rcd_plan = inx.fetchone()
      if rcd_plan != None:
            boollectura = (rcd_plan[8]).find('Lectura')
            booldiscurso = (rcd_plan[8]).find('Discurso')
            sexo='%masculino%'
            sexo2='%MASCULINO%'
            #    return render_template ( url_for ('topico_read'), pgmid_pm = pgmid_pm)
            if boollectura != -1 or booldiscurso != -1:
                return render_template ( url_for ('topico_read'))
            else:
                inx = cnx.cursor(buffered = True)
                stmt = """SELECT mstid, hstyear, hstmonth, hstname, hstid2, hstname2, hstasig, mstgenero, mststatus 
                FROM msthistori a, mststudent b where a.hstid = b.mstid"""
                inx.execute(stmt)
                rcd_hst_mst_all = inx.fetchall() 
                return render_template('Subtopicosfmxy.html', students = rcd_hst_mst_all, pgmid=pgmid_pm, 
                                   semanai = (rcd_plan[6]), semanaf = (rcd_plan[7]) , tipo= (rcd_plan[8]) )
      else:
          flash('No hay registro en la base programamensual')
          return redirect ( url_for ('topicos') )
  else:
        pass
  return redirect( url_for('Index'))


if __name__ == '__main__':
    app.run(port=3000, debug=True)

6587
