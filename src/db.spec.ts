import { afterAll, beforeAll, expect, setSystemTime, test } from "bun:test";
import { getLatestState, getUsersWhoShouldBeNotified, processData } from "./db";

beforeAll(() => {
  const date = new Date("1999-01-01T00:00:00.000Z");
  setSystemTime(date); // it's now January 1, 1999
});

afterAll(() => {
  setSystemTime();
});

test("processData", () => {
  const data = [
    { id: 123, timestamp: new Date().getTime(), euroJackpotLastmessage: 2 },
    {
      id: 123,
      timestamp: new Date().setMinutes(1),
      euroJackpotLastmessage: 3,
    },
    {
      id: 123,
      timestamp: new Date().setMinutes(2),
      lottoJackpotLastmessage: 3,
    },
    { id: 999, timestamp: new Date() },
  ];

  expect(processData({}, 123)).toBeNull();
  expect(processData(data, 9)).toBeNull();
  expect(processData(data, 123)).toStrictEqual({
    id: 123,
    timestamp: 915148920000,
    euroJackpotLastmessage: 3,
    lottoJackpotLastmessage: 3,
  });
});

test("getLatestState", () => {
  const data = [
    { id: 123, timestamp: new Date().getTime(), euroJackpotLastmessage: 2 },
    {
      id: 123,
      timestamp: new Date().setMinutes(2),
      lottoJackpotLastmessage: 3,
    },
    {
      id: 123,
      timestamp: new Date().setMinutes(1),
      euroJackpotLastmessage: 3,
    },
    { id: 999, timestamp: new Date().getTime() },
  ];

  expect(getLatestState({})).toStrictEqual([]);
  expect(getLatestState(data)).toStrictEqual([
    {
      id: 123,
      timestamp: 915148920000,
      euroJackpotLastmessage: 3,
      lottoJackpotLastmessage: 3,
    },
    { id: 999, timestamp: new Date().getTime() },
  ]);
});

test("getUsersWhoShouldBeNotified", () => {
  const data = [
    {
      id: 123,
      timestamp: new Date().getTime(),
      euroJackpotLastmessage: 10,
      eurojackpotBottomBound: 10,
    },
    {
      id: 123,
      timestamp: new Date().setMinutes(2),
      lottoJackpotLastmessage: 3,
    },
    {
      id: 999,
      timestamp: new Date().getTime(),
      euroJackpotLastmessage: 20,
      eurojackpotBottomBound: 10,
    },
    { id: 456, timestamp: new Date().getTime() },
  ];

  expect(getUsersWhoShouldBeNotified(20, "eurojackpot", data)).toStrictEqual([
    { id: 456, timestamp: new Date().getTime() },
    {
      id: 999,
      timestamp: new Date().getTime(),
      euroJackpotLastmessage: 20,
      eurojackpotBottomBound: 10,
    },
  ]);
});
