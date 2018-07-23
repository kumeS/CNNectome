from networks import unet, ops3d
import tensorflow as tf
import json


def train_net():
    input_shape = (43, 430, 430)
    raw = tf.placeholder(tf.float32, shape=input_shape)
    raw_batched = tf.reshape(raw, (1, 1,) + input_shape)

    last_fmap, fov, anisotropy = unet.unet(raw_batched, 12, 6, [[1, 3, 3], [1, 3, 3], [3, 3, 3]],
                                           [[(1, 3, 3), (1, 3, 3)], [(1, 3, 3), (1, 3, 3)],
                                            [(3, 3, 3), (3, 3, 3)], [(3, 3, 3), (3, 3, 3)]],
                                           [[(1, 3, 3), (1, 3, 3)], [(1, 3, 3), (1, 3, 3)],
                                            [(3, 3, 3), (3, 3, 3)], [(3, 3, 3), (3, 3, 3)]],
                                           voxel_size=(10, 1, 1), fov=(10, 1, 1))

    logits_batched, fov = ops3d.conv_pass(
        last_fmap,
        kernel_size=[[1, 1, 1]],
        num_fmaps=2,
        activation=None,
        fov=fov,
        voxel_size=anisotropy
    )

    output_shape_batched = logits_batched.get_shape().as_list()

    output_shape = output_shape_batched[1:]  # strip the batch dimension
    flat_logits = tf.transpose(tf.reshape(tensor=logits_batched, shape=(2,-1)))


    gt_labels = tf.placeholder(tf.float32, shape=output_shape[1:])
    gt_labels_flat = tf.reshape(gt_labels, (-1,))

    gt_bg = tf.to_float(tf.not_equal(gt_labels_flat, 1))
    flat_ohe = tf.stack(values=[gt_labels_flat, gt_bg], axis=1)

    loss_weights = tf.placeholder(tf.float32, shape=output_shape[1:])
    loss_weights_flat = tf.reshape(loss_weights, (-1,))
    print(logits_batched.get_shape().as_list())
    probabilities = tf.reshape(tf.nn.softmax(logits_batched, dim=1)[0], output_shape)
    predictions = tf.argmax(probabilities, axis=0)

    ce_loss_balanced = tf.losses.softmax_cross_entropy(flat_ohe, flat_logits, weights=loss_weights_flat)
    ce_loss_unbalanced = tf.losses.softmax_cross_entropy(flat_ohe, flat_logits)
    tf.summary.scalar('loss_balanced_syn', ce_loss_balanced)
    tf.summary.scalar('loss_unbalanced_syn', ce_loss_unbalanced)

    opt = tf.train.AdamOptimizer(
        learning_rate=0.5e-4,
        beta1=0.95,
        beta2=0.999,
        epsilon=1e-8)

    optimizer = opt.minimize(ce_loss_balanced)
    merged = tf.summary.merge_all()

    tf.train.export_meta_graph(filename='unet.meta')

    names = {
        'raw': raw.name,
        'probabilities': probabilities.name,
        'predictions': predictions.name,
        'gt_labels': gt_labels.name,
        'loss_balanced_syn': ce_loss_balanced.name,
        'loss_unbalanced_syn': ce_loss_unbalanced.name,
        'loss_weights': loss_weights.name,
        'optimizer': optimizer.name,
        'summary': merged.name}

    with open('net_io_names.json', 'w') as f:
        json.dump(names, f)


def inference_net():
    input_shape = (91, 862, 862)
    raw = tf.placeholder(tf.float32, shape=input_shape)
    raw_batched = tf.reshape(raw, (1, 1,) + input_shape)

    last_fmap, fov, anisotropy = unet.unet(raw_batched, 12, 6, [[1, 3, 3], [1, 3, 3], [3, 3, 3]],
                                           [[(1, 3, 3), (1, 3, 3)], [(1, 3, 3), (1, 3, 3)],
                                            [(3, 3, 3), (3, 3, 3)], [(3, 3, 3), (3, 3, 3)]],
                                           [[(1, 3, 3), (1, 3, 3)], [(1, 3, 3), (1, 3, 3)],
                                            [(3, 3, 3), (3, 3, 3)], [(3, 3, 3), (3, 3, 3)]],
                                           voxel_size=(10, 1, 1), fov=(10, 1, 1))

    logits_batched, fov = ops3d.conv_pass(
        last_fmap,
        kernel_size=[[1, 1, 1]],
        num_fmaps=2,
        activation=None,
        fov=fov,
        voxel_size=anisotropy
    )

    output_shape_batched = logits_batched.get_shape().as_list()

    output_shape = output_shape_batched[1:]  # strip the batch dimension

    probabilities = tf.reshape(tf.nn.softmax(logits_batched, dim=1)[0], output_shape)
    predictions = tf.argmax(probabilities, axis=0)
    print(probabilities.name)

    tf.train.export_meta_graph(filename='unet_inference.meta')


if __name__ == '__main__':
    train_net()
    tf.reset_default_graph()
    inference_net()
