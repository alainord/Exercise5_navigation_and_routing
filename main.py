import flet as ft


def main(page: ft.Page):
    page.title = "Exercise 5 - Navigation & Routing"
    page.window_width = 420
    page.window_height = 780
    page.theme_mode = ft.ThemeMode.LIGHT

    # Keep simple session state for passing data between routes
    if page.session.get("form_data") is None:
        page.session.set("form_data", {})

    # ------------- Common helpers -------------
    def back_to_previous_view(_=None):
        if len(page.views) > 1:
            page.views.pop()
            page.go(page.views[-1].route)

    def app_bar(title: str, show_back: bool = True):
        return ft.AppBar(
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=back_to_previous_view,
            ) if show_back else None,
            leading_width=40,
            title=ft.Text(title),
            center_title=False,
            actions=[],
        )


    # ------------- Route builders -------------
    def build_login_view():
        email = ft.TextField(label="Email", width=350)
        password = ft.TextField(label="Password", password=True, can_reveal_password=True, width=350)
        error_text = ft.Text(value="", color=ft.Colors.RED)

        def do_login(_):
            email.error_text = None
            password.error_text = None
            error_text.value = ""

            missing = []
            if not email.value:
                email.error_text = "Email is required"
                missing.append("email")
            if not password.value:
                password.error_text = "Password is required"
                missing.append("password")

            if missing:
                error_text.value = "Please enter " + " and ".join(missing)
                page.update()
                return

            page.go("/home")

        return ft.View(
            route="/login",
            appbar=app_bar("Login", show_back=False),
            controls=[
                ft.Container(height=8),
                ft.Column([
                    email,
                    password,
                    ft.ElevatedButton("Login", on_click=do_login, width=200),
                    error_text,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.START),
            ],
            padding=20,
        )

    def build_home_view():
        to_form_btn = ft.ElevatedButton("Go to Form", icon=ft.Icons.NAVIGATE_NEXT, on_click=lambda _: page.go("/form"))
        return ft.View(
            route="/home",
            appbar=app_bar("Home", show_back=True),
            controls=[
                ft.Container(height=12),
                ft.Column([
                    ft.Text("Welcome! Use the button below to fill the form.", size=16),
                    to_form_btn,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ],
            padding=20,
        )

    def build_form_view():
        # Fields
        name = ft.TextField(label="Full name", width=360)

        # Date of Birth via DatePicker
        dob_field = ft.TextField(label="Date of Birth", read_only=True, width=360)
        from datetime import date as _date
        dp = ft.DatePicker(
            first_date=_date(1900, 1, 1),
            last_date=_date(2100, 12, 31),
            on_change=lambda e: setattr(dob_field, "value", str(e.control.value)) or page.update(),
        )
        page.overlay.append(dp)

        def open_date_picker(_):
            dp.open = True
            page.update()

        gender_group = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(value="Male", label="Male"),
                ft.Radio(value="Female", label="Female"),
                ft.Radio(value="Other", label="Other"),
            ]),
        )

        address = ft.TextField(label="Address", multiline=True, min_lines=2, max_lines=4, width=360)

        country = ft.Dropdown(
            label="Country",
            options=[
                ft.dropdown.Option("Finland"),
                ft.dropdown.Option("Sweden"),
                ft.dropdown.Option("Norway"),
                ft.dropdown.Option("Estonia"),
                ft.dropdown.Option("Other"),
            ],
            width=360,
        )

        def submit_form(_):
            # minimal validation: require name and country
            name.error_text = None
            country.error_text = None

            if not name.value:
                name.error_text = "Name is required"
            if not country.value:
                country.error_text = "Select a country"

            page.update()
            if name.error_text or country.error_text:
                return

            data = {
                "name": name.value,
                "dob": dob_field.value,
                "gender": gender_group.value,
                "address": address.value,
                "country": country.value,
            }
            page.session.set("form_data", data)
            page.go("/details")

        return ft.View(
            route="/form",
            appbar=app_bar("Form", show_back=True),
            controls=[
                ft.Container(height=10),
                ft.Column([
                    name,
                    ft.Row([
                        dob_field,
                        ft.IconButton(icon=ft.Icons.DATE_RANGE, tooltip="Pick date", on_click=open_date_picker),
                    ]),
                    ft.Row([ft.Text("Gender:"), gender_group]),
                    address,
                    country,
                    ft.Container(height=6),
                    ft.ElevatedButton("Submit", on_click=submit_form, icon=ft.Icons.CHECK_CIRCLE),
                ], tight=True, expand=False),
            ],
            padding=20,
        )

    def build_details_view():
        data = page.session.get("form_data") or {}

        def info_row(label: str, value: str):
            return ft.Row([
                ft.Text(label + ":", weight=ft.FontWeight.W_600),
                ft.Text(value or "-"),
            ])

        card = ft.Card(
            elevation=3,
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.PERSON),
                        title=ft.Text(data.get("name") or "Details"),
                        subtitle=ft.Text("Submitted form details"),
                    ),
                    ft.Divider(),
                    info_row("Date of Birth", data.get("dob", "")),
                    info_row("Gender", data.get("gender", "")),
                    info_row("Address", data.get("address", "")),
                    info_row("Country", data.get("country", "")),
                ], tight=True),
                padding=16,
                width=360,
            ),
        )

        return ft.View(
            route="/details",
            appbar=app_bar("Details", show_back=True),
            controls=[
                ft.Container(height=10),
                ft.Column([
                    card,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ],
            padding=20,
        )

    # ------------- Navigation handlers -------------
    def route_change(route):
    # Solo construimos y añadimos la vista nueva, sin borrar las anteriores
        if page.route in ("/", "", None):
            page.go("/login")
            return

        if page.route == "/login":
            page.views.clear()
            page.views.append(build_login_view())

        elif page.route == "/home":
            v = build_home_view()
            page.views.append(v)

        elif page.route == "/form":
            v = build_form_view()
            page.views.append(v)

        elif page.route == "/details":
            v = build_details_view()
            page.views.append(v)

        else:
            page.views.append(build_login_view())

        # Refrescamos la vista actual
        page.update()

    def view_pop(view):
        back_to_previous_view()

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # initial route
    page.go(page.route or "/login")


if __name__ == "__main__":
    ft.app(target=main)
