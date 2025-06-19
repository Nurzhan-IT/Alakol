document.addEventListener("DOMContentLoaded", function () {
    const priceData = JSON.parse('{{ dynamic_price_json_data|safe|escapejs }}');
    // Removed console.log for priceData debugging (security improvement)
    const calendarBody = document.getElementById("calendar-body");

    // Получаем текущий месяц и год
    const today = new Date();
    const year = today.getFullYear();
    const month = today.getMonth(); // 0-11

    // Первый день месяца
    const firstDay = new Date(year, month, 1).getDay(); // 0 = воскресенье
    const firstWeekday = (firstDay === 0) ? 6 : firstDay - 1; // 0 = понедельник

    // Кол-во дней в месяце
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    let dateCounter = 1;
    for (let i = 0; i < 6; i++) {
        const row = document.createElement("tr");

        for (let j = 0; j < 7; j++) {
            const cell = document.createElement("td");

            if (i === 0 && j < firstWeekday) {
                cell.innerHTML = "";
            } else if (dateCounter > daysInMonth) {
                cell.innerHTML = "";
            } else {
                const fullDate = new Date(year, month, dateCounter);
                const dateStr = fullDate.toISOString().split("T")[0];

                cell.innerHTML = dateCounter;

                if (priceData[dateStr]) {
                    const priceSpan = document.createElement("span");
                    priceSpan.className = "day-price";
                    priceSpan.textContent = priceData[dateStr] + "₽";
                    cell.appendChild(document.createElement("br"));
                    cell.appendChild(priceSpan);
                }

                dateCounter++;
            }

            row.appendChild(cell);
        }

        calendarBody.appendChild(row);
        if (dateCounter > daysInMonth) break;
    }
});