(() => {
  const form = document.querySelector("#quote-form");
  if (!form) return;

  const level = form.querySelector("#id_finish_level");
  const serviceInputs = [...form.querySelectorAll("[data-service]")];
  const range = document.querySelector("#estimate-range");
  const subtotalOutput = document.querySelector("#estimate-subtotal");
  const feeOutput = document.querySelector("#estimate-fee");
  const levelOutput = document.querySelector("#estimate-level");
  const money = new Intl.NumberFormat("en-NP", {
    style: "currency",
    currency: "NPR",
    maximumFractionDigits: 0,
  });

  function recalculate() {
    const selectedLevel = level.value || "medium";
    const subtotal = serviceInputs.reduce((sum, input) => {
      const quantity = Math.max(0, Number.parseInt(input.value || "0", 10) || 0);
      const unitPrice = Number.parseInt(input.dataset[selectedLevel] || "0", 10);
      return sum + quantity * unitPrice;
    }, 0);
    const fee = Math.round(subtotal * 0.06);
    const midpoint = subtotal + fee;
    subtotalOutput.textContent = money.format(subtotal);
    feeOutput.textContent = money.format(fee);
    levelOutput.textContent = `${level.options[level.selectedIndex]?.text || "Medium"} specification.`;
    range.textContent = subtotal
      ? `${money.format(Math.round(midpoint * 0.9))} – ${money.format(Math.round(midpoint * 1.12))}`
      : "Select at least one service";
  }

  level.addEventListener("change", recalculate);
  serviceInputs.forEach((input) => input.addEventListener("input", recalculate));
  recalculate();
})();

