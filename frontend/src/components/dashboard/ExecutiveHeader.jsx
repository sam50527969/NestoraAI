import Card from "../ui/Card";

export default function ExecutiveHeader() {
  const hour = new Date().getHours();

  let greeting = "Good Evening";

  if (hour < 12) {
    greeting = "Good Morning";
  } else if (hour < 18) {
    greeting = "Good Afternoon";
  }

  return (
    <Card className="executive-header">
      <div>
        <p className="eyebrow">Executive Dashboard</p>

        <h1>{greeting}, Sam 👋</h1>

        <p>
          Here's your business overview and AI recommendations for today.
        </p>
      </div>
    </Card>
  );
}