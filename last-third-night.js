
// نور على نور - حساب الثلث الأخير من الليل

const NIGHT_REMINDER = {
  title: "🌙 قيام الليل | شوايل الآخرة",
  message: "🌙 دخل الثلث الأخير من الليل، وقت الدعاء والاستغفار والقيام. فلا تحرم نفسك من بركة هذا الوقت المبارك."
};

// maghrib و fajr تاريخان يتضمنان اليوم والوقت والمنطقة الزمنية الصحيحة
function calculateLastThird(maghrib, fajr) {
  const start = new Date(maghrib);
  const end = new Date(fajr);

  if (
    !Number.isFinite(start.getTime()) ||
    !Number.isFinite(end.getTime()) ||
    end <= start
  ) {
    throw new Error("يجب تحديد المغرب والفجر التالي له بصورة صحيحة.");
  }

  const nightDuration = end.getTime() - start.getTime();

  return new Date(end.getTime() - nightDuration / 3);
}

if (typeof module !== "undefined") {
  module.exports = { calculateLastThird, NIGHT_REMINDER };
}
