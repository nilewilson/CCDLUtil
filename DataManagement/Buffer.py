"""
This file is for EEG buffers
"""

import numpy as np
import CCDLUtil.Utility.AssertVal as AV


class MovingWindowBuffer(object):

    # todo -- this fails if data passed > 2d samples passed at a time.
    # todo -- test this method.

    def __init__(self, moving_window_size, num_channels, buffer_queue, out_queue, update_interval, internal_buffer_size=None):
        """
        A sample is defined as every read from the buffer_queue.
        A channel is a dimension along the data read from the buffer queue.

        An understanding of the internal workings of this object are needed to use it most wisely:
            The buffer stores data in the format (sample #, channel #).
            The buffer's actual size (not visible to the client) is preallocated (and never changes) to avoid problems
                with reallocating large portions of memory.  This size is controlled with 'internal_buffer_size'.

        :param moving_window_size:  The number of samples to save to the buffer.
        :param num_channels:  Number of channels of data (ie. size of the list placed on the buffer_queue)
        :param buffer_queue:  Buffer queue is the origin of the data.
                                Data passed to this queue should be a list or 1D np array.
                                
                                If 'start' is passed to this queue, we will clear the buffer_queue, then begin putting data on the queue
                                If 'stop' is passed to this queue, we will stop putting data on the queue and perpetually clear
                                    the buffer_queue
                                
        :param out_queue:  Queue to place data on after the buffer reaches moving_window_size.
        :param update_interval: On ever update_interval samples, the pervious moving_window_size samples are placed on the out_buffer_queue
        :param internal_buffer_size: The size to make the buffer internally.  If none, will be set to 20 * moving_window_size. Defaults to None
        """
        if internal_buffer_size is None:
            internal_buffer_size = 20 * moving_window_size
        self.moving_window_size, self.num_channels = moving_window_size, num_channels
        self.update_interval = update_interval
        self.internal_buffer_size = internal_buffer_size
        self.buffer = np.zeros((self.internal_buffer_size, self.num_channels))
        self.buffer_queue = buffer_queue
        self.out_queue = out_queue

    def start_buffer(self):
        """
         Starts the buffer, reading from buffer_queue and writing to out_buffer_queue
         once the buffer reaches moving_window_size.  Once the buffer reaches moving_window_size and is placed on the
         queue, the buffer is cleared.
        """
        # This is our lead and trailing storage indexes.  This means the data in our buffer (as seen by the client)
            # is self.buffer[trail_buffer_storage_index:lead_buffer_storage_index, :]
        lead_buffer_storage_index = -1  # Set to -1 so first update will make it 0. This avoids a fense-post problem.
        trail_buffer_storage_index = lead_buffer_storage_index - self.moving_window_size
        sample_index = 0
        while True:
            # We follow the algorithm
                # 1. Get new sample and update indexes
                # 2. Check if we need to adjust the buffer bounds
                # 3. Add sample to the buffer at sample_index
                # 4. Check if we need to put our buffer on the sample queue
                    # The buffer should be formatted so this can be done easily

            ###############################################
            #  Step 1 - Get new sample and update indexes #
            ###############################################
            sample_arr = self.buffer_queue.get()  # A blocking call
            if sample_arr == 'stop':
                # Reset our indexes.
                lead_buffer_storage_index = -1  # Set to -1 so first update will make it 0. This avoids a fense-post problem.
                trail_buffer_storage_index = lead_buffer_storage_index - self.moving_window_size
                sample_index = 0
                self.handle_stop()


            # This one we just collected is our nth sample.
            # Samples are zero based indexed
            sample_index += 1
            lead_buffer_storage_index += 1
            trail_buffer_storage_index += 1


            ############################################################
            #  Step 2  - Check if we need to adjust the buffer bounds  #
            ############################################################
            # Check if we're going to go over the buffer limit.
            if lead_buffer_storage_index == self.internal_buffer_size:
                # Fix buffer by coping over data.  We use self.moving_window_size - 1 because we have not yet
                # inserted the new data.
                self.buffer[0:self.moving_window_size - 1, :] = self.buffer[trail_buffer_storage_index: lead_buffer_storage_index - 1]
                # Reset our indexes.
                lead_buffer_storage_index = self.moving_window_size
                trail_buffer_storage_index = 0

            # Run some assertions
            AV.assert_less(lead_buffer_storage_index, self.internal_buffer_size)
            AV.assert_equal(lead_buffer_storage_index - trail_buffer_storage_index, self.moving_window_size)

            ############################################
            #  Step 3  - Add Add sample to the buffer  #
            ############################################
            self.buffer[lead_buffer_storage_index, :] = sample_arr


            #####################################################################
            #  Step 4 - Check if we need to put our buffer on the sample queue  #
            #####################################################################
            # Check if we need to put the buffer on the queue.
            if sample_index == self.update_interval:
                sub_buffer_to_send = self.buffer[trail_buffer_storage_index:lead_buffer_storage_index, :]
                AV.assert_equal(sub_buffer_to_send.shape[0], self.moving_window_size, message="Internal Error - buffer is incorrectly formatted")
                # Add our buffer to the queue.
                self.out_queue.put(sub_buffer_to_send)
                # Reset our sample index
                sample_index = 0

    def handle_stop(self):
        while True:
            sample_arr = self.buffer_queue.get()
            if sample_arr == 'start':
                return


class NonOverlappingBuffer(object):
    """
    A NoOverlap Buffer is a buffer that reads in data.  This is a more primitive version of the MovingWindowBuffer class.
    """

    def __init__(self, capacity, num_channels, buffer_queue, out_queue):
        """
        A sample is defined as every read from the buffer_queue.
        A channel is a dimension along the data read from the buffer queue.

        This nonoverlapping buffer stores moving_window_size samples and, once moving_window_size is reached, it places
        the results on the out_buffer_queue and flushes the buffer.
        :param capacity:  The number of samples to save to the buffer.
        :param num_channels:  Number of channels of data (ie. size of the list placed on the buffer_queue)
        :param buffer_queue:  Buffer queue is the origin of the data.
                                Data passed to this queue should be a list or 1D np array.
        :param out_queue:  Queue to place data on after the buffer reaches moving_window_size.
        """
        self.capacity, self.num_channels = capacity, num_channels
        self.buffer = np.zeros((self.capacity, self.num_channels))
        self.sample_index = 0
        self.buffer_queue = buffer_queue
        self.out_queue = out_queue

    def start_buffer(self):
        """
         Starts the buffer, reading from buffer_queue and writing to out_buffer_queue
         once the buffer reaches moving_window_size.  Once the buffer reaches moving_window_size and is placed on the
         queue, the buffer is cleared.
        """
        while True:
            arr = self.buffer_queue.get()  # A blocking call
            if self.sample_index % self.capacity == 0:  # check if we reached capcity
                if self.sample_index != 0:  # Make sure we aren't putting on an empty buffer.
                    self.out_queue.put(self.buffer)
                self.buffer = np.zeros((self.capacity, self.num_channels))
                self.buffer = arr  # Set our buffer to our new sample
            else:
                self.buffer = np.vstack((self.buffer, arr))
            self.sample_index += 1

