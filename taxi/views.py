from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import DriverCreationForm, CarCreationForm, LicenseUpdateForm, CarSearchForm, CarUpdateForm
from .models import Driver, Car, Manufacturer


@login_required
def index(request):
    """View function for the home page of the site."""

    num_drivers = Driver.objects.count()
    num_cars = Car.objects.count()
    num_manufacturers = Manufacturer.objects.count()

    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_drivers": num_drivers,
        "num_cars": num_cars,
        "num_manufacturers": num_manufacturers,
        "num_visits": num_visits + 1,
    }

    return render(request, "taxi/index.html", context=context)


class ManufacturerListView(LoginRequiredMixin, generic.ListView):
    model = Manufacturer
    context_object_name = "manufacturer_list"
    template_name = "taxi/manufacturer_list.html"
    paginate_by = 2


class ManufacturerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Manufacturer
    fields = "__all__"
    success_url = reverse_lazy("taxi:manufacturer-list")


class ManufacturerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Manufacturer
    fields = "__all__"
    success_url = reverse_lazy("taxi:manufacturer-list")


class ManufacturerDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Manufacturer
    success_url = reverse_lazy("taxi:manufacturer-list")


class CarListView(LoginRequiredMixin, generic.ListView):
    model = Car
    paginate_by = 2
    queryset = Car.objects.all().select_related("manufacturer")

    def get_context_data(self, *, object_list=None, **kwargs):
        contex = super(CarListView, self).get_context_data(**kwargs)
        contex["search_form"] = CarSearchForm()

        model = self.request.GET.get("model", "")

        contex["search_form"] = CarSearchForm(initial={
            "model": model
        })

        return contex

    def get_queryset(self):
        form = CarSearchForm(self.request.GET)

        if form.is_valid():
            return self.queryset.filter(
                model__icontains=form.cleaned_data["model"]
            )


class CarDetailView(LoginRequiredMixin, generic.DetailView):
    model = Car


class CarCreateView(LoginRequiredMixin, generic.CreateView):
    model = Car
    form_class = CarCreationForm
    success_url = reverse_lazy("taxi:car-list")


class CarUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Car
    # fields = "__all__"
    form_class = CarUpdateForm
    success_url = reverse_lazy("taxi:car-list")


class CarDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Car
    success_url = reverse_lazy("taxi:car-list")


class DriverListView(LoginRequiredMixin, generic.ListView):
    model = Driver
    paginate_by = 2


class DriverDetailView(LoginRequiredMixin, generic.DetailView):
    model = Driver
    queryset = Driver.objects.all().prefetch_related("cars__manufacturer")


class DriverCreateView(LoginRequiredMixin, generic.CreateView):
    model = Driver
    form_class = DriverCreationForm
    success_url = reverse_lazy("taxi:driver-list")


class DriverDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Driver
    success_url = reverse_lazy("taxi:driver-list")


class LicenseUpdateView(generic.UpdateView):
    model = Driver
    template_name = "taxi/license_form.html"
    form_class = LicenseUpdateForm
    success_url = reverse_lazy("taxi:driver-list")


@login_required
def assign_driver(request, pk):
    current_user = request.user
    if current_user in Car.objects.get(id=pk).drivers.all():
        Car.objects.get(id=pk).drivers.remove(current_user)
    else:
        Car.objects.get(id=pk).drivers.add(current_user)
    return redirect(f"cars/{pk}/")
