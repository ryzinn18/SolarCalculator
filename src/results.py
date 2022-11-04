from math import ceil
import numpy as np
import matplotlib.pyplot as plt


def calculate_mod_quantity(needed_kwh: int, mod_kwh: int) -> int:
    return ceil(needed_kwh / mod_kwh)


def calculate_savings(annual_prod: int) -> int:
    price_kwh = 0.28       #float(input("What is the cost (dollars) for a kWh? ")
    savings = annual_prod * price_kwh
    return round(savings)


def main(annual_cons, monthly_cons, annual_prod, monthly_prod, needed_kwh, mod_kwh):



class Results():
    
    def __init__(self):
        self.annual_cons = Consumption.payload["annual"]
        self.monthly_cons = Consumption.payload["monthly"]
        self.annual_prod = Production.payload["annual"]
        self.monthly_prod = Production.payload["monthly"]
        self.needed_kwh = Production.payload["dc_size"]
        self.mod_kwh = Production.payload["mod_kwh"]
        self.graph_dict = {"Consumption":self.monthly_cons,
                           "Production":self.monthly_prod}

        self.mod_quantity = self.get_mod_quantity()
        self.savings = self.calculate_savings()
        self.graph = self.get_graph()

    def get_mod_quantity(self):
        self.mod_quantity = self.needed_kwh / self.mod_kwh
        self.mod_quantity_fig = ceil(self.mod_quantity)
        print(f"{title} will need {self.mod_quantity_fig} mods.")
        return ceil(self.mod_quantity)

    def calculate_savings(self):
        self.price_kwh = 0.28       #float(input("What is the cost (dollars) for a kWh? ")
        self.savings = self.annual_prod * self.price_kwh
        self.savings_fig = round(self.savings)
        print(f"{title}'s total annual savings will be: ${self.savings_fig}")
        return round(self.savings_fig)

    def get_graph(self):
        fig = plt.figure()
        # ax = fig.add_axes([.11, .1, .85, .75])
        fig, ax = plt.subplots()
        #x = np.array(months["Int"])

        prod_y = np.array(self.graph_dict["Production"])
        cons_y = np.array(self.graph_dict["Consumption"])


        cons_graph = ax.bar(months["Str"], cons_y, width=1, color="orange",label="Consumption",edgecolor="black",capstyle='round')
        prod_graph = ax.plot(months["Str"], prod_y, "bo", label="Production", linestyle="--", linewidth=2, markersize=5)

        ax.bar_label(cons_graph, padding=-15)
        ax.set_ylabel('kWh')
        ax.set_facecolor('C0')
        ax.set_title(f"{title}'s Consumption vs Production", fontsize="x-large")
        legend = ax.legend(fontsize="large")
        legend.get_frame().set_color("xkcd:salmon")
        plt.tight_layout()


        plt.savefig('testGraph')
        plt.show()
