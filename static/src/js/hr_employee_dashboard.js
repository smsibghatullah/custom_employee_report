/**@odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";

const actionRegistry = registry.category("actions");

class HrEmployeeDashboard extends Component {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this._fetchEmployeeCounts();
    }

    async _fetchEmployeeCounts() {
        const result = await this.orm.call("hr.employee", "get_oman_employee_counts", [], {});

        // Update Company Name and Logo
        document.getElementById("company_logo").src = result.company_logo;
        document.getElementById("company_name").textContent = result.company_name;

        // Update Employee Counts
        document.getElementById("omani_count").textContent = result.total_omani;
        document.getElementById("non_omani_count").textContent = result.total_non_omani;

        // Update Age Distribution for Omani Employees
        document.getElementById("age_18_30_omani").textContent = result.age_18_30_omani;
        document.getElementById("age_31_40_omani").textContent = result.age_31_40_omani;
        document.getElementById("age_41_50_omani").textContent = result.age_41_50_omani;
        document.getElementById("age_51_60_omani").textContent = result.age_51_60_omani;
        document.getElementById("age_61_65_omani").textContent = result.age_61_65_omani;

        // Update Age Distribution for Non-Omani Employees
        document.getElementById("age_18_30_non_omani").textContent = result.age_18_30_non_omani;
        document.getElementById("age_31_40_non_omani").textContent = result.age_31_40_non_omani;
        document.getElementById("age_41_50_non_omani").textContent = result.age_41_50_non_omani;
        document.getElementById("age_51_60_non_omani").textContent = result.age_51_60_non_omani;
        document.getElementById("age_61_65_non_omani").textContent = result.age_61_65_non_omani;
    }
}

HrEmployeeDashboard.template = "my_module.HrEmployeeDashboard";
actionRegistry.add("hr_employee_dashboard", HrEmployeeDashboard);
