import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import $api from "../http";
import { AuthResponse } from "../models/response/AuthResponse";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import WordCloud from "react-d3-cloud";
import Comments from "./Comments";
import { Col, Row, Button } from "react-bootstrap";

interface PlotData {
  id: number;
  result: string;
  yt_id: string;
  user: number;
  type: number;
}

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

export const PlotPage: React.FC = () => {
  const { ytId } = useParams<{ ytId: string }>();
  const [plotData, setPlotData] = useState<PlotData[]>([]);
  const [emotion, setEmotion] = useState<number | undefined>(undefined);

  useEffect(() => {
    const fetchPlotData = async () => {
      try {
        const response = await $api.get<AuthResponse>("calculation-result/", {
          params: { yt_id: ytId },
        });
        setPlotData(response.data as unknown as PlotData[]);
        console.log(plotData);
      } catch (error) {
        console.error("Error fetching plot data:", error);
      }
    };

    fetchPlotData();
  }, [ytId]);

  const generatePlots = () => {
    if (!plotData || plotData.length === 0) return null;

    if (emotion)
      return (
        <div>
          <Button variant="primary" onClick={() => setEmotion(undefined)}>
            К метрикам
          </Button>
          <Comments yt_id={ytId} emotion_id={emotion} />
        </div>
      );

    return plotData.map((data) => {
      console.log(data);
      if (data.yt_id !== ytId) {
        return null;
      }
      if (data.type === 8) {
        const parsedResult = JSON.parse(data.result);
        const dates = parsedResult[0];
        const values = parsedResult[1];
        const chartData = dates.map((date: string, index: number) => ({
          date,
          value: values[index],
        }));

        return (
          <div key={data.id}>
            <h3>Cumulative count of comments</h3>
            <ResponsiveContainer width="50%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#8884d8"
                  activeDot={{ r: 8 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        );
      } else if (data.type === 9) {
        const parsedResult = JSON.parse(data.result);
        const chartData = Object.keys(parsedResult).map((key) => ({
          name: key,
          value: parsedResult[key],
        }));

        return (
          <div key={data.id}>
            <h3>Pie Chart for Type 8 Data</h3>
            <ResponsiveContainer width="50%" height={400}>
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  outerRadius={150}
                  fill="#8884d8"
                  dataKey="value"
                  label
                >
                  {chartData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        );
      } else if (data.type === 18) {
        const parsedResult = JSON.parse(data.result);

        const createWordCloudData = (freqData: { [key: string]: number }) =>
          Object.keys(freqData).map((key) => ({
            text: key,
            value: Math.log2(freqData[key]) * 5,
          }));

        const allFreqData = createWordCloudData(parsedResult.all_freq);
        const posFreqData = createWordCloudData(parsedResult.pos_freq);
        const negFreqData = createWordCloudData(parsedResult.neg_freq);
        console.log(allFreqData);
        return (
          <div key={data.id}>
            <h3>Word Cloud for Type 13 Data</h3>
            <div style={{ display: "flex", justifyContent: "space-around" }}>
              <div style={{ width: "30%" }}>
                <h4>All Frequencies</h4>
                <WordCloud data={allFreqData} width={300} height={300} />
              </div>
              <div style={{ width: "30%" }}>
                <h4>Positive Frequencies</h4>
                <WordCloud
                  data={posFreqData.slice(10)}
                  width={300}
                  height={300}
                />
              </div>
              <div style={{ width: "30%" }}>
                <h4>Negative Frequencies</h4>
                <WordCloud data={negFreqData} width={300} height={300} />
              </div>
            </div>
          </div>
        );
      } else if (data.type === 10) {
        const parsedResult = JSON.parse(data.result);

        console.log(parsedResult);

        return (
          <div>
            <ul>
              <li onClick={() => setEmotion(1)}>
                {"sadness: " + parsedResult.sadness}
              </li>
              <li onClick={() => setEmotion(2)}>
                {"joy: " + parsedResult.joy}
              </li>
              <li onClick={() => setEmotion(3)}>
                {"love: " + parsedResult.love}
              </li>
              <li onClick={() => setEmotion(4)}>
                {"anger: " + parsedResult.anger}
              </li>
              <li onClick={() => setEmotion(5)}>
                {"fear: " + parsedResult.fear}
              </li>
              <li onClick={() => setEmotion(6)}>
                {"surprise: " + parsedResult.surprise}
              </li>
              <li onClick={() => setEmotion(7)}>
                {"neutral: " + parsedResult.neutral}
              </li>
            </ul>
          </div>
        );
        // return <Comments />;
      }

      // return <div>kdjf</div>;
      // return <Comments />;
      return null;
    });
  };

  return <div className="plots">{generatePlots()}</div>;
};

export default PlotPage;
