from dataclasses import field, dataclass


@dataclass
class Agent:
    name: str
    # Positive total means you owe money, negative means you are owed money.
    total: int = 0


@dataclass
class Expense:
    payee: str
    liabilities: dict[str, int] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return sum(self.liabilities.values())


@dataclass
class Transfer:
    payer: Agent
    payee: Agent
    amount: int

    def __str__(self) -> str:
        return f"{self.payer.name} -> {self.payee.name}: {self.amount}"


@dataclass
class Settlement:
    transfers: list[Transfer] = field(default_factory=list)

    agent_dict: dict[str, Agent] = field(default_factory=dict)
    unresolved: list[Agent] = field(default_factory=list)

    def insert_or_get_agent(self, agent_name: str) -> Agent:
        if agent_name in self.agent_dict:
            agent = self.agent_dict[agent_name]
        else:
            agent = Agent(agent_name)
            self.agent_dict[agent_name] = agent
        return agent


def generate_settlement(expenses: list[Expense]) -> Settlement:
    settlement = Settlement()

    # Construct agent nodes
    for expense in expenses:
        for agent_names, amount in expense.liabilities.items():
            agent = settlement.insert_or_get_agent(agent_names)
            agent.total += amount
        agent = settlement.insert_or_get_agent(expense.payee)
        agent.total -= expense.total

    settlement.unresolved: list[Agent] = sorted(
        filter(lambda a: a.total != 0, settlement.agent_dict.values()),
        key=lambda a: a.total,
    )
    while len(settlement.unresolved):
        payee = settlement.unresolved[0]
        payer = settlement.unresolved[-1]

        # Calculate transfer
        amount = min(-payee.total, payer.total)
        transfer = Transfer(payer, payee, amount)
        settlement.transfers.append(transfer)

        payee.total += amount
        payer.total -= amount

        # Remove or move payer
        if payer.total == 0:
            settlement.unresolved.pop()
        else:
            i = -1
            while payer.total < settlement.unresolved[i - 1].total:
                settlement.unresolved[i], settlement.unresolved[i - 1] = (
                    settlement.unresolved[i - 1],
                    settlement.unresolved[i],
                )
                i -= 1

        if payee.total == 0:
            settlement.unresolved.pop(0)
        elif len(settlement.unresolved):
            i = 0
            while settlement.unresolved[i + 1].total < payee.total:
                settlement.unresolved[i + 1], settlement.unresolved[1] = (
                    settlement.unresolved[i],
                    settlement.unresolved[i + 1],
                )
                i += 1

    return settlement


if __name__ == "__main__":
    expenses = [
        Expense(
            "Bjørnar",
            {
                "Sebastian": 1,
                "Mikkel": 3,
                "Emma": 2,
                "Bjørnar": 3,
            },
        ),
        Expense(
            "Mikkel",
            {
                "Mikkel": 2,
                "Sebastian": 1,
            },
        ),
        Expense(
            "Emma",
            {
                "Emma": 1,
                "Mikkel": 2,
                "Sebastian": 5,
            },
        ),
    ]

    settlement = generate_settlement(expenses)
    print("\n".join(map(str, settlement.transfers)))
