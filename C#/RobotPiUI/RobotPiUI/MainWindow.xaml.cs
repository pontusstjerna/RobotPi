﻿using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace RobotPiUI
{
    /// <summary>
    /// Interaction logic for CustomCommands.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        Client client;
        RobotController rController;

        public MainWindow()
        {
            InitializeComponent();
           // System.Diagnostics.Trace.WriteLine("Test");
        }

        private void OnKeyDown(object sender, KeyEventArgs e)
        {
            if(rController != null)
            {
                rController.AddKeyDown(e.Key);
            }
        }

        private void OnKeyUp(object sender, KeyEventArgs e)
        {
            if (rController != null)
            {
                rController.AddKeyUp(e.Key);
            }
        }

        private void button_Click(object sender, RoutedEventArgs e)
        {
            string recieved = client.Send(textBox.Text);

            console.Text += recieved + '\n';

            textBox.Text = "";

            ConsoleScroll.ScrollToBottom();
        }

        private void Connect_Click(object sender, RoutedEventArgs e)
        {
            client = new Client();
            console.Text = client.Connect(IpAddress.Text, int.Parse(Port.Text)) + '\n';
            if (client.IsConnected())
            {
                SetLed(true);
                rController = new RobotController(client);
            }
            else
            {
                SetLed(false);
            }
        }

        private void Disconnect_Click(object sender, RoutedEventArgs e)
        {
            if(client != null)
            {
                console.Text = client.Send("quit");
                client.Close();
            }

            SetLed(false);
        }

        private void SetLed(bool green)
        {
            if (green)
            {
                RedLed.Fill = new SolidColorBrush(System.Windows.Media.Colors.DarkRed);
                GreenLed.Fill = new SolidColorBrush(System.Windows.Media.Colors.LightGreen);
            }
            else
            {
                RedLed.Fill = new SolidColorBrush(System.Windows.Media.Colors.Red);
                GreenLed.Fill = new SolidColorBrush(System.Windows.Media.Colors.DarkGreen);
            }
        }

        private void Window_Closing(object sender, CancelEventArgs e)
        {
            if(client != null)
            {
                client.Send("quit");
                client.Close();
            }
        }
    }
}