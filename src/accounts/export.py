import csv
import xlwt
from django.http import HttpResponse
from .models import Account, OrgUser, InvoiceHistory


def export_member_list_csv(request):
    admin = request.user
    member_list = get_members_list(admin)

    return do_csv(['Username', 'Name', 'Email', 'Amount Owed', 'Amount Paid'], member_list, "members_list")


def export_member_list_excel(request):
    admin = request.user
    history_list = get_members_list(admin)

    return do_excel(['Username', 'Name', 'Email', 'Amount Owed', 'Amount Paid'],
                    history_list, "members_list", "Members")


def export_admin_history_csv(request):
    admin = request.user
    history_list = get_invoice_list(admin, True)

    return do_csv(['Date', 'Username', 'Description', 'Amount'], history_list, "history")


def export_admin_history_excel(request):
    admin = request.user
    history_list = get_invoice_list(admin, True)

    return do_excel(['Date', 'Username', 'Description', 'Amount'], history_list, "history", "History")


def export_member_history_csv(request):
    member = request.user
    history_list = get_invoice_list(member, False)

    return do_csv(['Date', 'Description', 'Amount'], history_list, "history")


def export_member_history_excel(request):
    member = request.user
    history_list = get_invoice_list(member, False)

    return do_excel(['Date', 'Description', 'Amount'], history_list, 'history', "History")


def do_csv(header, data, filename):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)

    writer = csv.writer(response)
    writer.writerow(header)

    for i in data:
        writer.writerow(i)

    return response


def do_excel(header, data, filename, sheet):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="{}.xls"'.format(filename)

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet(sheet)

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = header

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    member_list = data

    for row in member_list:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


def get_invoice_list(user, is_admin):
    if is_admin:
        history_list = InvoiceHistory.objects.filter(organization_name=user.organization_name)
    else:
        history_list = InvoiceHistory.objects.filter(username=user.username)

    new_history_list = []

    if is_admin:
        for history in history_list:
            history_date = str(history.date_sent)
            date = history_date.split(" ")
            tmp = [date[0], history.username, history.description, history.invoice_amount]
            new_history_list.append(tmp)
    else:
        for history in history_list:
            history_date = str(history.date_sent)
            date = history_date.split(" ")
            tmp = [date[0], history.description, history.invoice_amount]
            new_history_list.append(tmp)

    return new_history_list


def get_members_list(admin):
    member_list = OrgUser.objects.exclude(username=admin.username).filter(organization_name=admin.organization_name)
    new_member_list = []

    for member in member_list:
        name = member.first_name + "" + member.last_name
        tmp = [member.username, name, member.email, member.amount_owed, member.amount_paid]
        new_member_list.append(tmp)

    return new_member_list
