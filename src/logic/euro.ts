import {
  getUsersWhoShouldBeNotified,
  messageSent,
  setEurojackpot,
} from "../db";
import { sendMessage } from "./telegram";

const url = "https://www.lotto.de/api/stats/entities.eurojackpot/last";

export async function fetchEuroJackpot() {
  const response = await fetch(url);
  const body = await response.json();
  return body as { jackpotNew: number; drawDate: string };
}

export async function pollEurojackpot() {
  console.log("Poll Eurojackpot");
  const response = await fetchEuroJackpot();
  const jackpot = response.jackpotNew;
  const users = getUsersWhoShouldBeNotified(jackpot, "eurojackpot");

  await Promise.all(
    users.map((user) =>
      sendMessage(user.id, `Current Euro jackpot is ${jackpot}`)
    )
  );
  await messageSent(users, jackpot, "euroJackpotLastmessage");
  await setEurojackpot(jackpot);
}
