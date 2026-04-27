/** @odoo-module **/

console.log("LUXON DATE PATCH LOADED");

const { DateTime } = luxon;

// backup original (safety)
const originalToLocaleString = DateTime.prototype.toLocaleString;

// override
DateTime.prototype.toLocaleString = function (formatOpts) {
    try {
        const d = this.toJSDate();

        const dd = String(d.getDate()).padStart(2, "0");
        const mm = String(d.getMonth() + 1).padStart(2, "0");
        const yy = String(d.getFullYear()).slice(-2);

        const hh = String(d.getHours()).padStart(2, "0");
        const min = String(d.getMinutes()).padStart(2, "0");

        // datetime detect
        if (formatOpts && (formatOpts.hour || formatOpts.minute)) {
            return `${dd}/${mm}/${yy} ${hh}:${min}`;
        }

        // date only
        return `${dd}/${mm}/${yy}`;

    } catch (e) {
        return originalToLocaleString.call(this, formatOpts);
    }
};