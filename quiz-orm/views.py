from flask import render_template, request, redirect, url_for, abort, flash
from app import app
from models import Pytanie, Odpowiedz
from forms import *


@app.route('/')
def index():
    """Strona główna"""
    return render_template('index.html')


@app.route('/lista')
def lista():
    """Pobranie wszystkich pytań z bazy i zwrócenie szablonu z listą pytań"""
    pytania = Pytanie().select()

    if not pytania.count():
        flash('Brak pytań w bazie.', 'kom')
        return redirect(url_for('index'))

    return render_template('lista.html', pytania=pytania)


def flash_errors(form):
    """Odczytanie wszystkich błędów formularza i przygotowanie komunikatów"""
    for field, errors in form.errors.items():
        for error in errors:
            if type(error) is list:
                error = error[0]
            flash("Błąd: {}. Pole: {}".format(
                error,
                getattr(form, field).label.text))


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    """Wyświetlenie pytań i odpowiedzi w formie quizu oraz ocena poprawności
    przesłanych odpowiedzi"""
    if request.method == 'POST':
        print(request.form)
        wynik = 0
        for pid, odp in request.form.items():
            odpok = Pytanie.select(Pytanie.odpok).where(
                Pytanie.id == int(pid)).scalar()
            if odp == odpok:
                wynik += 1

        flash(f'Liczba poprawnych odpowiedzi, to: {wynik}', 'sukces')
        return redirect(url_for('index'))

    # GET, wyświetl pytania
    pytania = Pytanie().select()
    if not pytania.count():
        flash('Brak pytań w bazie.', 'kom')
        return redirect(url_for('index'))

    return render_template('quiz.html', pytania=pytania)


@app.route('/dodaj', methods=['GET', 'POST'])
def dodaj():
    """Dodawanie pytań i odpowiedzi"""
    form = DodajForm()
    print(form.odpowiedzi.data)
    print(form.pytanie.data)
    print(form.odpok.data)
    if form.validate_on_submit():
        odp = form.odpowiedzi.data
        p = Pytanie(pytanie=form.pytanie.data, odpok=odp[int(form.odpok.data)])
        p.save()
        for o in odp:
            inst = Odpowiedz(pnr=p.id, odpowiedz=o)
            inst.save()
        flash("Dodano pytanie: {}".format(form.pytanie.data))
        return redirect(url_for("lista"))
    elif request.method == 'POST':
        flash_errors(form)

    return render_template("dodaj.html", form=form, radio=list(form.odpok))
